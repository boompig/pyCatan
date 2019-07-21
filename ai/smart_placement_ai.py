from .ai import AI
from game_engine import Game
from typing import Tuple, Dict, List, Optional, Set, Iterator
import random
from hex import Hex
from catan_types import Vertex, Edge
import logging
from catan_gen import CatanConstants


logger = logging.getLogger(__name__)


class SmartPlacementAI(AI):

	def __init__(self, color: str, game: Game) -> None:
		super().__init__()
		self._color = color
		self._vertex_probs = {}  # type: Dict[int, List[Vertex]]
		self._prepare(game)

	def _prepare(self, game: Game) -> None:
		'''Prepare the AI by letting it calculate most probable settlements.'''

		for v in game.get_nodes():
			n = self._eval_vertex_value(game, v)
			if n not in self._vertex_probs:
				self._vertex_probs[n] = []
			self._vertex_probs[n].append(v)

	def _eval_vertex_value(self, game: Game, v: Tuple[int, int]) -> int:
		'''Evaluate the value of the given vertex.
		This is done by adding all the dots of the adjacent hexes.
		This is a rough measure of probability.'''

		n = 0

		for hex in game._vertex_map[v]:
			n += hex.get_num_dots()

		return n

	def get_road_placement(self, game: Game, settlement_vertex: Vertex) -> Edge:
		'''Return a random road stemming from settlement located at v.'''

		adjacent_v_set = game.get_adjacent_vertices(settlement_vertex)
		random.shuffle(list(adjacent_v_set))

		for v2 in adjacent_v_set:
			if not game.has_road(settlement_vertex, v2):
			   return (settlement_vertex, v2) # the road was built

		raise Exception("this is bad")

	def _eval_hex_robber_score(self, game: Game, hex: Hex, color: str) -> int:
		'''Return the robber score for this hex.
		Hex gets a point value of 0 if `color` is on it.
		Neutral hexes get a point-value of 1 for tie-break.
		Also 0 is the previous robber hex.'''

		score = 1 # neutral hexes get 1 point

		if hex == game.get_robber_hex():
			return 0

		for v in hex.get_vertices():
			if v in game._settlements:
				s = game._settlements[v]

				if s.color() == color:
					return 0 # no points for hexes with same color as choosing player
				elif s.is_city():
					score += 2 * hex.get_num_dots()
				else :
					score += 1 * hex.get_num_dots()

		return score

	def get_robber_pick(self, game: Game) -> str:
		'''Return a color to steal from. This is random.'''

		l = []

		for v in game.get_robber_hex().get_vertices():
			if v in game._settlements:
				l.append(game._settlements[v].color())
		if l == []:
			raise Exception("this is bad")
		else:
			return random.choice(l)

	def get_robber_placement(self, game: Game, color: str) -> Vertex:
		'''Return the *position* of the hex on which to place the robber.
		Should be a high-producing hex with no settlements/cities by this player.
		Color is the color of the player placing the robber.'''

		max_score = 0
		best_hex = None

		for row_i, row in enumerate(game._board):
			for col, hex in enumerate(row):
				score = self._eval_hex_robber_score(game, hex, color)
				if score > max_score:
					#best_hex = hex
					best_hex = (row_i, col)
					max_score = score
		assert best_hex is not None
		return best_hex

	def get_settlement_placement(self, game: Game) -> Vertex:
		'''Return the settlement with the highest combined prob. of generating a resource.'''

		sorted_vals = list(self._vertex_probs.keys())
		assert sorted_vals != []
		sorted_vals.sort(reverse=True)
		s = game.available_settlement_set

		# this has to go through all of them...
		for val in sorted_vals:
			for v in self._vertex_probs[val]:
				if v in s:
					return v
			# all of these are now off the table
			del(self._vertex_probs[val])
		raise Exception("this is bad")

	def robber_discard(self, game: Game, color: str) -> List[str]:
		'''Discard random cards from the player's hand.
		Return those cards.
		Right now discards random cards'''

		player = game.get_player(color)
		n = player.get_num_resources()
		gone_list = []
		while n > 7:
			# get the available resources
			l = []
			for r, count in player.get_hand().items():
				l.extend([r] * count)
			r = random.choice(l)
			player.deduct_resources([r])
			gone_list.append(r)
			n -= 1
		return gone_list

	def __get_available_settlement_vertices(self, game: Game) -> Set[Vertex]:
		player = game.get_player(self._color)
		# the simplest way is probably to get all the vertices from the roads
		potential_vs = player.get_road_vertices()
		good_vs = potential_vs.intersection(game.available_settlement_set)
		return good_vs

	def __get_upgradable_settlements(self, game: Game) -> List[Vertex]:
		l = []
		player = game.get_player(self._color)
		for v, s in player._settlements.items():
			if s.is_city():
				l.append(v)
		return l

	def __get_available_road_placements(self, game: Game) -> Iterator[Edge]:
		player = game.get_player(self._color)
		for vertex in player.get_road_vertices():
			for v2 in game.get_adjacent_vertices(vertex):
				if game.can_place_road(vertex, v2, self._color):
					yield (vertex, v2)

	def __get_playable_cards(self, game: Game) -> List[str]:
		player = game.get_player(self._color)
		playable_cards = []
		for card, num in player.get_development_cards().items():
			if card != "VP" and num > 0:
				playable_cards.extend([card] * num)
		return playable_cards

	def do_turn(self, game: Game) -> None:
		player = game.get_player(self._color)

		'''
		playable_cards = self.__get_playable_cards(game)
		if playable_cards != []:
			card = random.choice(playable_cards)
			d = {
				"play": "development card",
				"card": card
			}
			if card == "monopoly":
				d["target_resource"]
				# get the resource
		'''

		# preference for development cards
		cost = CatanConstants.development_card_cost
		if player.can_deduct_resources(cost):
			game.get_development_card(self._color)

		# next try to build a settlement
		available_settlement_vertices = self.__get_available_settlement_vertices(game)
		if len(available_settlement_vertices) > 0:
			cost = CatanConstants.building_costs["settlement"]
			if player.can_deduct_resources(cost):
				v = random.choice(list(available_settlement_vertices))
				game.add_settlement(v, self._color)

		# city
		upgradable_settlements = self.__get_upgradable_settlements(game)
		if len(upgradable_settlements) > 0:
			cost = CatanConstants.building_costs["city"]
			if player.can_deduct_resources(cost):
				v = random.choice(list(upgradable_settlements))
				game.add_city(v, self._color)

		# road
		cost = CatanConstants.building_costs["road"]
		if player.can_deduct_resources(cost):
			# find a spare place to build it
			places = [edge for edge in self.__get_available_road_placements(game)]
			if places == []:
				# logging.debug(f"nowhere to place a new road for player {self.color}")
				pass
			else:
				road = random.choice(places)
				game.add_road(road[0], road[1], self._color)

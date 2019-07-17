from game_engine import Game
import random
from typing import List, Optional, Set, Iterator
from catan_types import Vertex, Edge
from catan_gen import CatanConstants
import logging


logger = logging.getLogger(__name__)


class TestAI:
	def __init__(self, color: str):
		self.color = color

	def get_settlement_placement(self, game: Game) -> Vertex:
		# find all the available
		possible_vertices = list(game.available_settlement_set)
		v = random.choice(possible_vertices)
		return v

	def get_road_placement(self, game: Game, settlement_placement: Vertex) -> Edge:
		l = []
		for v2 in game.get_adjacent_vertices(settlement_placement):
			road = (settlement_placement, v2)
			if game.can_place_road(road[0], road[1], self.color):
				l.append(road)
		assert l != []
		return random.choice(l)

	def __get_available_settlement_vertices(self, game: Game) -> Set[Vertex]:
		player = game.get_player(self.color)
		# the simplest way is probably to get all the vertices from the roads
		potential_vs = player.get_road_vertices()
		good_vs = potential_vs.intersection(game.available_settlement_set)
		return good_vs

	def __get_upgradable_settlements(self, game: Game) -> List[Vertex]:
		l = []
		player = game.get_player(self.color)
		for v, s in player._settlements.items():
			if s.is_city():
				l.append(v)
		return l

	def __get_available_road_placements(self, game: Game) -> Iterator[Edge]:
		player = game.get_player(self.color)
		for vertex in player.get_road_vertices():
			for v2 in game.get_adjacent_vertices(vertex):
				if game.can_place_road(vertex, v2, self.color):
					yield (vertex, v2)

	def get_structure_to_buy(self, game: Game) -> Optional[dict]:
		player = game.get_player(self.color)

		# preference for development cards
		cost = CatanConstants.development_card_cost
		if player.can_deduct_resources(cost) and game.has_development_cards():
			return {
				"purchase": "development card"
			}

		# next try to build a settlement
		available_settlement_vertices = self.__get_available_settlement_vertices(game)
		if len(available_settlement_vertices) > 0:
			cost = CatanConstants.building_costs["settlement"]
			if player.can_deduct_resources(cost):
				return {
					"purchase": "settlement",
					"placement": random.choice(list(available_settlement_vertices))
				}

		# city
		upgradable_settlements = self.__get_upgradable_settlements(game)
		if len(upgradable_settlements) > 0:
			cost = CatanConstants.building_costs["city"]
			if player.can_deduct_resources(cost):
				return {
					"purchase": "city",
					"placement": random.choice(list(upgradable_settlements))
				}

		# road
		cost = CatanConstants.building_costs["road"]
		if player.can_deduct_resources(cost):
			# find a spare place to build it
			places = [edge for edge in self.__get_available_road_placements(game)]
			if places == []:
				# logging.debug(f"nowhere to place a new road for player {self.color}")
				pass
			else:
				return {
					"purchase": "road",
					"placement": random.choice(places)
				}

		return None

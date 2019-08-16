from game_engine import Game
import random
from typing import List, Optional, Tuple
from catan_types import Vertex, Edge, HexCoord
import logging
from .ai import AI


logger = logging.getLogger(__name__)


class DummyAI(AI):
	def __init__(self, color: str, game: Game):
		self._color = color

	def get_settlement_placement(self, game: Game) -> Vertex:
		# find all the available
		possible_vertices = list(game.available_settlement_set)
		v = random.choice(possible_vertices)
		return v

	def get_road_placement(self, game: Game, settlement_placement: Vertex) -> Edge:
		l = []
		for v2 in game.get_adjacent_vertices(settlement_placement):
			road = (settlement_placement, v2)
			if game.can_place_road(road[0], road[1], self._color):
				l.append(road)
		assert l != []
		return random.choice(l)

	def do_turn(self, game: Game) -> None:
		return None

	def get_robber_placement(self, game: Game) -> Tuple[Optional[str], HexCoord]:
		# get a random hex
		d = game.get_board()
		hexes = [coord for coord in d.values()]
		current_robber_hex = game.get_robber_hex()
		hexes.remove(current_robber_hex)

		target_color = None
		stop = False
		while not stop:
			target_hex = random.choice(hexes)
			colors = game.get_players_on_hex(target_hex)
			if len(colors) == 0:
				target_color = None
				stop = True
			elif len(colors) > 1:
				if self._color in colors:
					colors.remove(self._color)
				target_color = random.choice(colors)
				stop = True

		return target_color, target_hex.get_coord()

	def robber_discard(self, game: Game) -> List[str]:
		'''Discard down to 7 cards'''
		player = game.get_player(self._color)
		num_resources = player.get_num_resources()
		discard = []  # type: List[str]
		if num_resources > 7:
			num_discard = num_resources - 7
			hand = player.get_hand()
			r_list = []
			for r, n in hand.items():
				r_list.extend([r] * n)
			discard = random.sample(r_list, num_discard)
			player.deduct_resources(discard)
		assert player.get_num_resources() <= 7
		return discard
from game_engine import Game
import random
from typing import List, Optional, Set, Iterator
from catan_types import Vertex, Edge
from catan_gen import CatanConstants
import logging
from .ai import AI


logger = logging.getLogger(__name__)


class DummyAI(AI):
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

	def do_turn(self, game: Game) -> None:
		return None

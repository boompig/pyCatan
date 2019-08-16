from ai.dummy_ai import DummyAI
from game_engine import Game
from catan_tk import CatanApp
import logging


LATTICE = CatanApp.get_hex_coord_lattice()
COLORS = ["red", "white", "blue"]
logging.basicConfig(level=logging.DEBUG)


def test_get_robber_placement():
	"""Just make sure this method works"""
	game = Game("red", COLORS, LATTICE)
	ai = DummyAI("red", game)
	ai.get_robber_placement(game)


def test_get_settlement_placement():
	"""Just make sure this method works"""
	game = Game("red", COLORS, LATTICE)
	ai = DummyAI("red", game)
	ai.get_settlement_placement(game)


def test_get_road_placement():
	"""Just make sure this method works"""
	game = Game("red", COLORS, LATTICE)
	ai = DummyAI("red", game)
	v = ai.get_settlement_placement(game)
	game.add_settlement(v, "red", initial_placement=True)
	ai.get_road_placement(game, v)


def test_robber_discard():
	"""Just make sure this method works"""
	game = Game("red", COLORS, LATTICE)
	ai = DummyAI("red", game)
	ai.robber_discard(game)
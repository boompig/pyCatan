from ai.smart_placement_ai import SmartPlacementAI
from game_engine import Game
from catan_tk import CatanApp

LATTICE = CatanApp.get_hex_coord_lattice()
COLORS = ["red", "orange", "green", "blue"]


def test_robber_discard():
	"""
	Make sure that robber_discard does in fact discard down to 7 cards
	"""
	game = Game(
		starting_color="orange",
		colors=COLORS,
		hex_coord_lattice=LATTICE
	)
	color = game.get_current_color()
	player = game.get_player(color)
	resources = ["ore"] * 10
	player.add_resources(resources)
	assert player.get_num_resources() > 7
	ai = SmartPlacementAI(color, game)
	ai.robber_discard(game)
	assert player.get_num_resources() <= 7

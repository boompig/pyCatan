from ai.smart_placement_ai import SmartPlacementAI
from game_engine import Game
from catan_tk import CatanApp


def test_robber():
	lattice = CatanApp.get_hex_coord_lattice()
	game = Game(
		starting_color="orange",
		colors=["red", "orange", "green", "blue"],
		hex_coord_lattice=lattice
	)
	color = game.get_current_color()
	player = game.get_player(color)
	resources = ["ore"] * 10
	player.add_resources(resources)
	assert player.get_num_resources() > 7
	ai = SmartPlacementAI(color, game)
	ai.robber_discard(game)
	assert player.get_num_resources() <= 7

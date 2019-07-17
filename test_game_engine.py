from game_engine import Game
import random
from catan_tk import CatanApp
from typing import List
from ai_for_testing import TestAI
import math


def floor(x: float):
	return int(math.floor(x))


def _automate_placement(ais, game: Game, colors: List[str]):
	for i in range(2):
		for color in colors:
			ai = ais[color]
			v = ai.get_settlement_placement(game)
			game.add_settlement(v, color)
			road = ai.get_road_placement(game, v)
			game.add_road(v, road[1], color, ignore_cost=True)


def test_game_ends():
	# predictable tests
	random.seed(42)
	colors = ["orange", "yellow", "green", "red"]
	ais = { color: TestAI(color) for color in colors }
	lattice = CatanApp.get_hex_coord_lattice()
	game = Game(
		starting_color="red",
		colors=colors,
		hex_coord_lattice=lattice
	)
	MAX_TURN = 10000
	_automate_placement(ais, game, colors)
	game.end_initial_placement()
	print("initial placement finished")

	turn = 0
	last_move_turn = -1

	while not game.is_game_over and turn < MAX_TURN and (turn - last_move_turn) < 200:
		color = game.get_current_color()
		roll = game.roll_dice()
		player = game.get_player(color)
		print(f"[Round {floor(turn / 4) + 1}] {color} ({player.get_num_vp()} points) rolled {roll}")
		# create a very simple strategy

		color = game.get_current_color()
		ai = ais[color]

		stop = False
		while not stop:
			structure =  ai.get_structure_to_buy(game)
			# print(structure)
			if structure:
				last_move_turn = turn
				if structure["purchase"] == "road":
					game.add_road(structure["placement"][0], structure["placement"][1], color)
				elif structure["purchase"] == "city":
					game.add_city(structure["placement"], color)
				elif structure["purchase"] == "settlement":
					game.add_settlement(structure["placement"], color)
				elif structure["purchase"] == "development card":
					game.get_development_card(color)
				else:
					raise Exception()
			else:
				stop = True
		game.next_turn()
		turn += 1

	# print details
	print("-" * 60)
	for color, player in game._players.items():
		print(f"[{color}] - {player.get_num_vp()} points")


	print("last made a move on turn %s" % last_move_turn)
	assert turn < MAX_TURN


if __name__ == "__main__":
	import logging
	import coloredlogs
	logging.basicConfig(level=logging.DEBUG)
	coloredlogs.install(level=logging.DEBUG)

	test_game_ends()
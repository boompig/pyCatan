from game_engine import Game, GameState
import random
from catan_tk import CatanApp
from typing import List
from ai.dummy_ai import DummyAI
from ai.smart_placement_ai import SmartPlacementAI
import math


COLORS = ["orange", "yellow", "green", "red"]
LATTICE = CatanApp.get_hex_coord_lattice()


def floor(x: float):
	return int(math.floor(x))


def _automate_placement(ais, game: Game, colors: List[str]):
	l = []
	MAX_TRIES = 100
	tries = 0
	while game.get_state() == GameState.INITIAL_PLACEMENT:
		color = game.get_current_color()
		l.append(color)
		ai = ais[color]
		v = ai.get_settlement_placement(game)
		game.add_settlement(v, color, initial_placement=True)
		road = ai.get_road_placement(game, v)
		game.add_road(road[0], road[1], color, initial_placement=True)
		game.next_turn()
		assert len(l) <= len(colors) * 2
		# this is just to make sure that we don't stay here forever
		tries += 1
		assert tries < MAX_TRIES


def test_game_ends():
	# predictable tests
	random.seed(42)
	game = Game(
		starting_color="red",
		colors=COLORS,
		hex_coord_lattice=LATTICE
	)
	ais = {}
	for i, color in enumerate(COLORS):
		if i == 0:
			ais[color] = SmartPlacementAI(color, game)
		else:
			ais[color] = DummyAI(color)

	MAX_TURN = 10000
	_automate_placement(ais, game, COLORS)
	print("initial placement finished")

	turn = 0
	last_move_turn = -1

	while not game.is_game_over and turn < MAX_TURN and (turn - last_move_turn) < 200:
		color = game.get_current_color()
		print(turn)
		roll = game.roll_dice()
		player = game.get_player(color)
		print(f"[Round {floor(turn / 4) + 1}] {color} ({player.get_num_vp()} points) rolled {roll}")
		color = game.get_current_color()
		ai = ais[color]
		ai.do_turn(game)
		game.next_turn()
		turn += 1
	# print details
	print("-" * 60)
	for color, player in game._players.items():
		print(f"[{color}] - {player.get_num_vp()} points")
	print("last made a move on turn %s" % last_move_turn)
	assert turn < MAX_TURN
	assert game.is_game_over


def test_initial_placement():
	random.seed(42)
	game = Game(
		"orange",
		COLORS,
		LATTICE
	)
	l = []
	ais = { color: DummyAI(color) for color in COLORS }
	while game.get_state() == GameState.INITIAL_PLACEMENT:
		color = game.get_current_color()
		l.append(color)
		ai = ais[color]
		v = ai.get_settlement_placement(game)
		game.add_settlement(v, color, initial_placement=True)
		road = ai.get_road_placement(game, v)
		game.add_road(road[0], road[1], color, initial_placement=True)
		game.next_turn()
		if len(l) > 8:
			break
	assert len(l) == 8
	expected = COLORS.copy()
	for color in reversed(COLORS):
		expected.append(color)
	assert l == expected


def test_play_knight_card():
	random.seed(42)
	game = Game(
		"orange",
		COLORS,
		LATTICE
	)
	ais = { color: DummyAI(color) for color in COLORS }
	_automate_placement(ais, game, COLORS)
	# give the first
	player = game.get_player("orange")
	player.add_development_card("knight")
	red_count = game.get_player("red").get_num_resources()
	orange_count = game.get_player("orange").get_num_resources()
	game.play_development_card("orange", "knight", {
		"target_color": "red"
	})
	assert game.get_player("red").get_num_resources() == red_count - 1
	assert game.get_player("orange").get_num_resources() == orange_count + 1


if __name__ == "__main__":
	import logging
	import coloredlogs
	logging.basicConfig(level=logging.DEBUG)
	coloredlogs.install(level=logging.DEBUG)

	test_game_ends()
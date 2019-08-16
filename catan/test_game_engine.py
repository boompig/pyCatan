from game_engine import Game, GameState
import random
from catan_tk import CatanApp
from typing import List
from ai.dummy_ai import DummyAI
from ai.smart_placement_ai import SmartPlacementAI
import math
from unittest import mock


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
			ais[color] = DummyAI(color, game)

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
		if roll == 7:
			steal_from_player, robber_hex = ai.get_robber_placement(game)
			game.move_robber(robber_hex, steal_from_player, moving_player=color)
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
	ais = { color: DummyAI(color, game) for color in COLORS }
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
	ais = { color: DummyAI(color, game) for color in COLORS }
	_automate_placement(ais, game, COLORS)

	# this is done so 7 is not rolled
	m = mock.MagicMock(return_value=1)
	with mock.patch("random.randint", m):
		roll = game.roll_dice()
		assert roll == 2

		player = game.get_player("orange")
		player.add_development_card("knight")
		red_count = game.get_player("red").get_num_resources()
		orange_count = game.get_player("orange").get_num_resources()
		green_player = game.get_player("green")
		# this should always be true regardless of placement
		assert green_player.get_num_resources() >= 1
		green_settlement_v = green_player.get_settlement(0).vertex()
		target_hex = game.get_hexes_for_vertex(green_settlement_v)[0]
		game.play_development_card("orange", "knight", {
			"target_color": "red",
			"target_hex": target_hex.get_coord()
		})
		assert game.get_player("red").get_num_resources() == red_count - 1
		assert game.get_player("orange").get_num_resources() == orange_count + 1


def test_play_monopoly_card():
	random.seed(42)
	game = Game(
		"orange",
		COLORS,
		LATTICE
	)
	ais = { color: DummyAI(color, game) for color in COLORS }
	_automate_placement(ais, game, COLORS)

	# this is done so 7 is not rolled
	m = mock.MagicMock(return_value=1)
	with mock.patch("random.randint", m):
		roll = game.roll_dice()
		assert roll == 2

		orange_player = game.get_player("orange")
		orange_player.add_development_card("monopoly")
		orange_hand = orange_player.get_hand()
		# remove any ore in the source player's hand
		if "ore" in orange_hand:
			orange_player.deduct_resources(["ore"] * orange_hand["ore"])

		total = 0
		old_totals = {}
		num_ores = {}
		for color in game.get_colors():
			player = game.get_player(color)
			if color == "orange":
				old_totals[color] = player.get_num_resources()
				continue
			hand = player.get_hand()
			if "ore" in hand:
				player.deduct_resources(["ore"] * hand["ore"])
			assert hand.get("ore", 0) == 0
			n = random.randint(1, 10)
			player.add_resources(["ore"] * n)
			old_totals[color] = player.get_num_resources()
			assert player.get_hand()["ore"] == n
			num_ores[color] = n
			total += n

		game.play_development_card("orange", "monopoly", {
			"target_resource": "ore"
		})
		for color in game.get_colors():
			print(color)
			player = game.get_player(color)
			if color == "orange":
				assert player.get_hand().get("ore", 0) == total
				assert player.get_num_resources() == old_totals["orange"] + total
			else:
				assert player.get_hand().get("ore", 0) == 0
				assert player.get_num_resources() == old_totals[color] - num_ores[color]


def test_play_road_building_card():
	random.seed(42)
	game = Game(
		"orange",
		COLORS,
		LATTICE
	)
	ais = { color: DummyAI(color, game) for color in COLORS }
	_automate_placement(ais, game, COLORS)
	color = game.get_current_color()
	player = game.get_player(color)

	assert player.get_num_roads() == 2

	# this is done so 7 is not rolled
	m = mock.MagicMock(return_value=1)
	with mock.patch("random.randint", m):
		roll = game.roll_dice()
		assert roll == 2

		player.add_development_card("road building")
		# build out from one of the initially placed roads, away from settlements
		roads = []

		source_road = player._roads[1]
		source_vertex = None
		bad_vertex = None
		if player.has_settlement_at(source_road[0]):
			bad_vertex = source_road[0]
			source_vertex = source_road[1]
		else:
			bad_vertex = source_road[1]
			source_vertex = source_road[0]
		possible_vs = game.get_adjacent_vertices(source_vertex)
		possible_vs.remove(bad_vertex)
		assert len(possible_vs) > 0
		to_v = possible_vs.pop()

		# first road
		roads.append((source_vertex, to_v))

		# second road builds again from the source road
		# note that this can run into settlements, other roads, and suchlike conditions
		possible_vs = game.get_adjacent_vertices(to_v)
		possible_vs.remove(source_vertex)
		assert len(possible_vs) > 0
		to_v_2 = possible_vs.pop()

		# second road
		roads.append((to_v, to_v_2))

		game.play_development_card(color, "road building", {
			"roads": roads
		})

		assert player.get_num_roads() == 4


def test_play_year_of_plenty():
	random.seed(42)
	game = Game(
		"orange",
		COLORS,
		LATTICE
	)
	ais = { color: DummyAI(color, game) for color in COLORS }
	_automate_placement(ais, game, COLORS)
	color = game.get_current_color()
	player = game.get_player(color)

	# this is done so 7 is not rolled
	m = mock.MagicMock(return_value=1)
	with mock.patch("random.randint", m):
		roll = game.roll_dice()
		assert roll == 2

		n = player.get_num_resources()
		assert n <= 3

		player.add_development_card("year of plenty")
		game.play_development_card(color, "year of plenty", {
			"resources": ["ore", "wheat"]
		})

		assert player.get_num_resources() == n + 2


def test_largest_army():
	random.seed(42)
	color = COLORS[0]
	game = Game(color, COLORS, LATTICE)
	ais = { color: DummyAI(color, game) for color in COLORS }
	_automate_placement(ais, game, COLORS)
	player = game.get_player(color)

	# from the 2 initial settlements
	assert player.get_num_vp() == 2

	player.add_development_card("knight")
	player.add_development_card("knight")
	player.add_development_card("knight")

	# after the initial placement need to find a list of distinct target hexes
	target_hexes = {}
	for c in COLORS[1:]:
		p = game.get_player(c)
		for v in p.get_settlement_vertices():
			hexes = game.get_hexes_for_vertex(v)
			for hex in hexes:
				hex_coord = hex.get_coord()
				if hex_coord not in target_hexes:
					target_hexes[hex_coord] = c

	for i in range(3 * len(COLORS)):
		# make sure 7 not rolled
		m = mock.MagicMock(return_value=1)
		with mock.patch("random.randint", m):
			roll = game.roll_dice()
			assert roll == 2

		if i % len(COLORS) == 0:
			# remove the position of the current robber
			robber_hex = game.get_robber_hex_coords()
			if robber_hex in target_hexes:
				target_hexes.pop(robber_hex)

			# choose a random hex to target
			target_hex = random.choice([hex for hex in target_hexes])
			target_color = target_hexes[target_hex]

			game.play_development_card("orange", "knight", {
				"target_color": target_color,
				"target_hex": target_hex
			})
			game.next_turn()
		else:
			# do nothing
			game.next_turn()

	assert player.get_num_knights_played() == 3
	assert player.has_special_card("largest army")

	# 2 from initial settlements and 2 from largest army
	assert player.get_num_vp() == 4


def test_add_city():
	random.seed(42)
	color = COLORS[0]
	game = Game(color, COLORS, LATTICE)
	ais = { color: DummyAI(color, game) for color in COLORS }
	_automate_placement(ais, game, COLORS)
	player = game.get_player(color)

	m = mock.MagicMock(return_value=1)
	with mock.patch("random.randint", m):
		roll = game.roll_dice()
		assert roll == 2

	# add enough resources to upgrade a settlement to a city
	player.add_resources(["wheat"] * 2 + ["ore"] * 3)
	# pick a random city for this player, doesn't matter which one
	v = random.choice(player.get_settlement_vertices())

	assert player.get_num_vp() == 2

	game.add_city(v, color)

	assert player.get_num_vp() == 3

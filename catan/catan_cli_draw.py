from game_engine import Game
from hex import Hex
import sys


def draw_ascii_hex_nums(game: Game):
	def f(hex: Hex):
		t = hex.get_number()
		if t == -1:
			return "__"
		else:
			return str(t).ljust(2)

	for row in game.get_map():
		if len(row) == 3:
			print("  ".join([f(hex) for hex in row]))
		elif len(row) == 2:
			print("  " + "  ".join([f(hex) for hex in row]) + "  ")
		elif len(row) == 1:
			print((2 * "  ") + f(row[0]) + (2 * "  "))


def draw_ascii_hex_tokens(game: Game):
	'''Render the board in a terminal.
	This helps visualize the tokens'''

	def f(hex):
		t = hex.get_token()
		if t == '':
			return " _"
		else:
			return t.ljust(2)

	for row in game.get_map():
		if len(row) == 3:
			print("  ".join([f(hex) for hex in row]))
		elif len(row) == 2:
			print("  " + "  ".join([f(hex) for hex in row]) + "  ")
		elif len(row) == 1:
			print((2 * "  ") + f(row[0]) + (2 * "  "))


def draw_ascii_settlements(game: Game):
	board = game.get_map()
	vertices = game.get_nodes()

	# max_y will be found on the bottom-most hex
	max_y = board[-1][0].get_bottom()
	# max_x will be found at the hex in row 3 on the right
	max_x = board[2][-1].get_right()

	min_y = board[0][0].get_top()
	assert min_y >= 0
	min_x = board[2][0].get_left()
	print(f"min: ({min_x}, {min_y})")

	assert max_x > 1
	assert max_y > 1
	print(f"max: ({max_x}, {max_y})")

	road_chars = {}

	for y in range(min_y, max_y + 1):
		for x in range(0, max_x + 1):
			v = (x, y)
			if v in vertices:
				s = game.get_settlement_at_vertex(v)
				outgoing_roads = game.get_roads_from_vertex(v)
				if s:
					if s.is_city():
						print(s.color()[0].upper() + "c", end="")
					else:
						print(s.color()[0].upper() + "s", end="")
				else:
					print(" .", end="")

				if outgoing_roads != []:
					# potentially schedule the road
					# schedule it only if it has not yet been scheduled
					for (road, color) in outgoing_roads:
						road_x = int((road[0][0] + road[1][0]) / 2)
						road_y = int((road[0][1] + road[1][1]) / 2)
						road_chars[(road_x, road_y)] = color
			elif v in road_chars:
				color = road_chars[v]
				print(f"{color[0]}r", end="")
			else:
				print("  ", end="")
		print("")
	sys.stdout.flush()
'''
Phases of the game:
1. Place settlement and road.
	- settlement placement is in order of players
	- road placement is right after settlement placement and must be adjacent
	- settlements must be at least 2 vertices away from each other
	- order matters - resources are immediately dispensed

2. Dice rolls
	- tiles in play are ones with settlements on them
	- settlements can never be taken off
	- only tiles with rolled numbers are relevant
	- tiles can have multiple owners

3. New placements
	- house must observe distance rules, also now must be on road (of same color)
		- I think I need a coordinate system of some sort
		- maybe keep a list of REACHED vertices, cross-reference with available ones when asking if can place


	- since houses can never be taken off, can keep track of available vertices

	- cities must be placed on top of houses (I can keep track of this pretty easily)

	- must keep track of roads for length purposes
	- must determine when a road is blocked (can have special event for that)
	- determine connection based on settlements, etc.

4. Development cards

5. Robber
	- disposing of cards
	-


some things to consider:
	- see if I can get GPU do some computation


How do I deal with this?
I need to keep

5 columns (not full), 5 full rows, 4 half-rows

RULES
adjacent is (x + 1, y - 0.5), (x + 1, y + 0.5), (x - 1, y + 0.5), (x - 1, y - 0.5), (x, y - 1), (x, y + 1)

why do I care? I need to determine distance...
keep a list of all vertices

I need to keep track of line positions
TOP = 0o
THEN 1w 2s 3b 4o 5o 6s 7s 8w 9s(b)
10w(b) = BOTTOM

LEFT = 0b
THEN 1b 2bw 3bw 4wws 5wso 6osd 7sdb 8dbb 9db 10b
RIGHT = 11b


(0, 0) -->

'''

import random
from board import Board

class Engine():


	def __init__(self):
		'''Create a new engine (i.e. game)
		'''

		# create the board
		self.b = Board()

	def initial_placement(self):
		'''Perform the initial placement of settlements/roads.'''

		# key is...?

	def roll(self):
		'''Roll the dice.'''

		roll = random.randint(1, 6) + random.randint(1, 6)

		print("Rolled {}".format(roll))

		# depending on the roll, show which resources will be given out
		return self.b.get_rolled_tile(roll)

if __name__ == "__main__":
	e = Engine()

	for i in range(5):
		print(e.roll())


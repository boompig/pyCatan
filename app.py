'''
Consider using 3D
Consider using images and sprites
'''

#################
#	IMPORTS		#
#################

from tkinter import *
from utils import *
import random

class DiceDrawer():
	dot_radius = 9
	dice_length = 100

	def __init__(self, offset):
		self._offset = offset

	def draw_die(self, canvas, number, color):
		self._coords = self.get_cube_coords(0, 0, DiceDrawer.dice_length)

		tkint = to_tkinter_coords(self._coords, App.height, self._offset)
		corners = (tkint[0], tkint[1], tkint[-2], tkint[-1])

		# create a rectangle
		canvas.create_rectangle(
			*corners,
			fill = color,
			outline = "black"
		)

		if color == "red":
			spot_color = "black"
		else:
			spot_color = "red"

		self.draw_num(canvas, number, spot_color)

	def draw_dice(self, canvas, number1 = 1, number2 = 6):
		self.draw_die(canvas, number1, "yellow")
		self._offset = (self._offset[0] * 2 + DiceDrawer.dice_length, self._offset[1])
		self.draw_die(canvas, number2, "red")

	def draw_num(self, canvas, number, spot_color):
		if number % 2:
			self.draw_dot(canvas, "center", spot_color)

			if number > 1:
				self.draw_dot(canvas, "left_low", spot_color)
				self.draw_dot(canvas, "right_high", spot_color)

			if number > 3:
				self.draw_dot(canvas, "left_high", spot_color)
				self.draw_dot(canvas, "right_low", spot_color)
		else:
			self.draw_dot(canvas, "left_low", spot_color)
			self.draw_dot(canvas, "right_high", spot_color)

			if number > 2:
				self.draw_dot(canvas, "left_high", spot_color)
				self.draw_dot(canvas, "right_low", spot_color)

			if number > 4:
				self.draw_dot(canvas, "center_left", spot_color)
				self.draw_dot(canvas, "center_right", spot_color)

	def draw_dot(self, canvas, orient, spot_color):
		if "center" in orient:
			y_ratio = x_ratio = .5

		if "left" in orient:
			x_ratio = .25
		elif "right" in orient:
			x_ratio = .75

		if "low" in orient:
			y_ratio = .25
		elif "high" in orient:
			y_ratio = .75

		x = int((self._coords[0][0] + self._coords[-1][0]) * x_ratio)
		y = int((self._coords[0][1] + self._coords[-1][1]) * y_ratio)

		if spot_color == "red":
			circle_color = "black"
		else:
			circle_color = "white"

		canvas.create_oval (
			*to_tkinter_coords(
				((x - DiceDrawer.dot_radius, y - DiceDrawer.dot_radius), (x + DiceDrawer.dot_radius, y + DiceDrawer.dot_radius)),
				App.height,
				self._offset
			),
			fill=spot_color,
			outline=circle_color
		)

	def get_cube_coords(self, x1, y1, side_length):
		return (
			(x1, y1),
			(x1, y1 + side_length),
			(x1 + side_length, y1),
			(x1 + side_length, y1 + side_length),
		)

def scale_to_width(lower, middle, top):
	all_coords = lower + middle + top
	max_width = max(x for x, y in all_coords)

	l = []
	ratio = 100.0 / max_width

	for part in [lower, middle, top]:
		q = []

		for coord in part:
			new_coord = (int(coord[0] * ratio), int(coord[1] * ratio))
			q.append(new_coord)

		l.append(tuple(q))

	return l

class App():
	'''So there is my robber sprite.'''

	height = 300
	width = 350

	v_offset = 50
	h_offset = 50

	players = ["red", "green", "blue"]

	def __init__(self):
		self._root = Tk()

		self._offset = (App.h_offset, App.v_offset)

		self._canvas = Canvas(self._root, width=App.width, height=App.height)
		self._canvas.pack()

		# self.draw_dice()
		# self.draw_turn_label()

		lower = (
			(12, 7),
			#(0, 100),
			(38, 20),
			#(50, 0)
		)

		middle = (
			(10, 10),
			(40, 60)
		)

		top = (
			(15, 55),
			(35, 75)
		)

		l, m, t = scale_to_width(lower, middle, top)

		self.draw_robber(l, m, t)
		#self.roll_dice()
		#self.play_game()

	def draw_robber(self, lower, middle, top):
		self._canvas.create_oval(
			*to_tkinter_coords(lower, App.height, self._offset),
			fill="black"
		)

		self._canvas.create_oval(
			*to_tkinter_coords(middle, App.height, self._offset),
			fill="black"
		)

		self._canvas.create_oval(
			*to_tkinter_coords(top, App.height, self._offset),
			fill="black"
		)

	def draw_dice(self):
		'''Draw dice and associated button.'''

		# the roll
		self._v = StringVar()
		l = Label(self._root, textvariable=self._v)
		l.pack()

		# the button to roll
		b = Button(self._root, text="Roll!", command=self.roll_dice)
		b.pack()

	def draw_turn_label(self):
		'''Draw the label for current turn.'''

		self._turn_label = self._canvas.create_text(100, 100, text="")
		self._turn = 0

	def play_game(self):
		while self._n != 6:
			pass

		print("game over")

	def next_turn(self):
		self._turn = (self._turn + 1) % 3

	def set_turn(self):
		self._canvas.itemconfigure(self._turn_label, text="It is {}'s turn".format(self.players[self._turn]))

	def roll_dice(self):
		n1, n2 = random.randint(1, 6), random.randint(1, 6)

		self._n = n1 + n2

		self._v.set(str(self._n))
		d = DiceDrawer(self._offset)
		d.draw_dice(self._canvas, n1, n2)

		self.next_turn()
		self.set_turn()

	def run(self):
		self._root.mainloop()

if __name__ == "__main__":
	a = App()

	a.run()


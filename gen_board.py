#############################
#	Written by Daniel Kats	#
#	December 25, 2012		#
#############################

'''
This file is concerned with generating the board.
1. Catan board w/ Resources
	- done
2. Board with tokens

3. Place buildings
	- set.
	- upgrade set. to city
	- road
	
	- different colors
	
4. Place robber

THEN IDK
'''

#############
#	IMPORTS	#
#############

from Tkinter import *
from catan_gen import CatanConstants, CatanRenderConstants
import random
from sys import exit as sys_exit
from hex import Hex
from collections import deque

def get_tkinter_coords(normal_person_coords):
	'''Works on lists, too.'''
	
	return reduce(tuple.__add__, normal_person_coords)
	
def get_hex_coords(x_0, y_0, minor_horiz_dist, major_horiz_dist, minor_vert_dist):
	'''Given certain parameters for the hexagon, return tuple of vertices for hexagon.'''

	return (
		(x_0, y_0), 
		(x_0 + minor_horiz_dist, y_0 + minor_vert_dist), 
		(x_0 + minor_horiz_dist + major_horiz_dist, y_0 + minor_vert_dist), 
		(x_0 + 2 * minor_horiz_dist + major_horiz_dist, y_0), 
		(x_0 + minor_horiz_dist + major_horiz_dist, y_0 - minor_vert_dist), 
		(x_0 + minor_horiz_dist, y_0 - minor_vert_dist),
	)
	
def get_hex_row(x_0, y_0, minor_horiz_dist, major_horiz_dist, minor_vert_dist, num):
	hexes = []
	
	for i in range(num):
		if len(hexes) > 0:
			x_0, y_0 = hexes[-1][3]
			x_0 += major_horiz_dist

		hexes.append(get_hex_coords(x_0, y_0, minor_horiz_dist, major_horiz_dist, minor_vert_dist))
	return hexes
	
def get_hex_latice(x_0, y_0, minor_horiz_dist, major_horiz_dist, minor_vert_dist):
	rows = []
	decr_set = set([1, 2, 4, 6])
	incr = minor_horiz_dist + major_horiz_dist
	
	for row_num, num_cols in enumerate(CatanConstants.tile_layout):
		if len(rows) > 0:
			x_0, y_0 = rows[-1][0][0]
			y_0 += minor_vert_dist
	
			if row_num in decr_set:
				x_0 -= incr
			else:
				x_0 += incr
	
		rows.append(get_hex_row(x_0, y_0, minor_horiz_dist, major_horiz_dist, minor_vert_dist, num_cols))
		
	return rows
	
def draw_hex_row(canvas, hex_row_coords, deck):
	'''Draw a horizontal row of hexagons given a list of tuples, each tuple representing the coordinates of the hexagon.'''

	tile_latice = []
	
	for hex_i, hex_v in enumerate(hex_row_coords):
		resource = deck.pop()
		canvas.create_polygon(*get_tkinter_coords(hex_v), fill=CatanRenderConstants.resource_color_map[resource], outline="black")
		#draw_token(canvas, hex_v, 12)
		tile_latice.append(resource)
	return tile_latice
		
def draw_token_latice(canvas, hex_latice_coords, hex_latice_model):
	unplaced_layout = {row : val for row, val in enumerate(CatanConstants.tile_layout)}
	
	# starting (back, 2)
	x_front = False
	row = 2
	letter = "a"
	inc = 1
	#print max(unplaced_layout.keys())
	
	# TODO we need to know if there is a desert associated with the thing
	
	while letter <= max(CatanConstants.token_map.keys()):
		col = (-1 * inc if x_front else inc - 1)
		
		if hex_latice_model[row][col] != "desert":
			draw_token(canvas, hex_latice_coords[row][col], letter)#CatanConstants.token_map[letter])
			letter = chr(ord(letter) + 1)
		
		unplaced_layout[row] -= 1
		
		# remove entirely placed rows
		if unplaced_layout[row] == 0:
			#print "Deleting row %d" % row
			del(unplaced_layout[row])
		#else:
			#print "unplaced at %d = %d" % (row, unplaced_layout[row])
		
		# stops lines below from glitching
		if len(unplaced_layout) == 0:
			break
		
		if row == 0:
			x_front = True
		elif row >= max(unplaced_layout.keys()):
			x_front = False
		
		if x_front:
			row += 1
		else:
			row -= 1
			
		while (row not in unplaced_layout) and len(unplaced_layout) > 0:
			if row == 0:
				x_front = True
			elif row == max(unplaced_layout.keys()):
				x_front = False
		
			if x_front:
				row += 1
			else:
				row -= 1
			
		if row == 2 and not x_front:
			inc += 1
		
		
def draw_token(canvas, hex_v, number):
	'''Given the hex coords, draw the token.'''
	
	padding = 5
	
	center = ((hex_v[0][0] + hex_v[4][0]) / 2, (hex_v[1][1] + hex_v[-1][1]) / 2)
	adjusted_center = (
		hex_v[1][0] + CatanApp.major_horiz_dist / 2,
		center[1],
	)
						
	
	canvas.create_oval(
		hex_v[1][0] + padding, 
		center[1] - CatanApp.major_horiz_dist / 2 + padding, 
		hex_v[2][0] - padding, 
		center[1] + CatanApp.major_horiz_dist / 2 - padding, 
		outline="black", 
		fill="white"
	)

	t = CatanConstants.token_map[number]
	canvas.create_text(adjusted_center, text=str(t))

		
def draw_hex_latice(canvas, hex_latice_coords):
	deck = CatanConstants.get_resource_distribution_pool()
	random.shuffle(deck)
	hex_latice = []

	for hex_row_coords in hex_latice_coords:
		hex_latice.append(draw_hex_row(canvas, hex_row_coords, deck))
		
	return hex_latice

class MapGen():
	'''Engine for generating Catan maps.'''

	def __init__(self):
		self._decr_set = set([1, 2, 4, 6])

	def gen(self):
		# this is a mapping of rows to hexes...
		self._board = []
		
		# create hexes with resources, shuffle
		deck = self._make_deck()

		# arrange deck on the board (so create placement)
		self._place_tiles(deck)

		# assign tokens
		self._assign_tokens()

		# and draw it
		self.draw()

	def _assign_tokens(self):
		'''Assign tokens to the tiles on the board.'''

		# a reversed list of letters (so pop operation works)
		letters = deque(reversed(sorted(CatanConstants.token_map.keys())))
		unplaced_layout = { row : col for row, col in enumerate(CatanConstants.tile_layout) }

		# start in corner (0, 2)
		row = 2
		col = 0
		outside_radius = 0
		print min(unplaced_layout.keys())
		
		# do this for all the letters
		while len(letters) > 0:
			print letters[-1]
			print "(%d, %d)" % (col, row)
			print unplaced_layout
			
			# withdraw a letter from the map
			if self._board[row][col].get_resource() != "desert":
				#self._board[row][col].set_token(CatanConstants.token_map[letters.pop()])
				self._board[row][col].set_token(letters.pop())
			
			unplaced_layout[row] -= 1

			if unplaced_layout[row] == 0:
				del(unplaced_layout[row])

			if len(unplaced_layout) > 0:
				row, col = self._get_next_tile(row, col, unplaced_layout)


	def _get_next_tile(self, row, col, unplaced_layout):
		# calculate next tile position
		if row <= min(unplaced_layout.keys()) - 1 and col >= 0:
			# reverse direction
			print "changing direction"
			col = -1 * col - 1
		elif row >= max(unplaced_layout.keys()) + 1 and col < 0:
			col = (1 + col) * -1

		if col >= 0:
			row -= 1
		elif col < 0:
			row += 1

		if row == 2 and col >= 0:
			col += 1

		if row in unplaced_layout:
			return (row, col)
		else:
			return self._get_next_tile(row, col, unplaced_layout)

	def _place_tiles(self, deck):
		'''Place tiles on the board.'''

		for row_num, num_cols in enumerate(CatanConstants.tile_layout):
			row = []
			self._board.append(row)

			for col in range(num_cols):
				row.append(Hex(deck.pop()))
		
	def _make_deck(self):
		'''Return a shuffled deck of unplaced resources.'''

		deck = CatanConstants.get_resource_distribution_pool()
		random.shuffle(deck)
		return deck

	def draw(self):
		'''Render the board.'''

		pass
		
		
class CatanApp():
	'''The Catan App (for now).
	For now side distances are determined statically. Can dynamically allocate them at a later point.'''
	
	height = 550
	width = 510
	minor_horiz_dist = 30
	major_horiz_dist = 60
	minor_vert_dist = 50
	render_start = (200, minor_vert_dist + 20)

	
	def __init__(self):
		self._master = Tk()
	
		# frame
		frame = Frame(self._master, width=CatanApp.width, height=CatanApp.height)
		#frame.bind("<Key>", self.key_pressed)
		# keys to end game
		frame.bind("<Escape>", self.end)
		frame.bind("<Return>", self.end)
		frame.bind("<space>", self.end)
		frame.focus_set() # this is very important
		frame.pack()

		# canvas
		w = Canvas(frame, width=CatanApp.width, height=CatanApp.height)
		w.pack()
		
		# latice AKA board
		self._hex_coord_latice = get_hex_latice(
			CatanApp.render_start[0], 
			CatanApp.render_start[1], 
			CatanApp.minor_horiz_dist, 
			CatanApp.major_horiz_dist, 
			CatanApp.minor_vert_dist
		)
		
		self._hex_latice = draw_hex_latice(w, self._hex_coord_latice)
		draw_token_latice(w, self._hex_coord_latice, self._hex_latice)
		
	def key_pressed(self, event):
		print repr(event.char)

	def end(self, event):
		print "exit event captured"
		self._master.destroy()
		#sys_exit(0)
	
	def run(self):
		self._master.mainloop()
	
def gen_map():
	mg = MapGen()
	mg.gen()

	b = mg._board

	for row in b:
		for col in row:
			print col.get_token(), 
		print ""

def render_map():
	app = CatanApp()
	app.run()

if __name__ == "__main__":
	#render_map()
	gen_map()

	
	

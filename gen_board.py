#############################
#	Written by Daniel Kats	#
#	December 25, 2012		#
#############################

'''
This file is improperly named - it is mainly concerned with:
	- the 'view' aspect (i.e. representation of board on screen)
	- the 'control' aspect (i.e. responding to user-caused events such as button clicks)
	
TODO break up the view and control portions
'''

#############
#	IMPORTS	#
#############

from Tkinter import *
from catan_gen import CatanConstants, CatanRenderConstants
from sys import exit as sys_exit
from hex import Hex
from map_gen import MapGen
from utils import *
from render import *
import random

class GamePhases():
	'''TODO for now, this is unused.'''
	
	first_settlement = "Place a settlement"
	first_road = "Place a road"
	
def get_hex_coords(x_0, y_0, minor_horiz_dist, major_horiz_dist, minor_vert_dist):
	'''Given certain parameters for the hexagon, return tuple of vertices for hexagon.'''
	
	# TODO move under class

	return (
		(x_0, y_0), 
		(x_0 + minor_horiz_dist, y_0 + minor_vert_dist), 
		(x_0 + minor_horiz_dist + major_horiz_dist, y_0 + minor_vert_dist), 
		(x_0 + 2 * minor_horiz_dist + major_horiz_dist, y_0), 
		(x_0 + minor_horiz_dist + major_horiz_dist, y_0 - minor_vert_dist), 
		(x_0 + minor_horiz_dist, y_0 - minor_vert_dist),
	)
	
def get_hex_row(x_0, y_0, minor_horiz_dist, major_horiz_dist, minor_vert_dist, num):
	'''Return list of hex row coordinates. num is the number of hexes in this row.'''
	
	# TODO move under class
	
	hexes = []
	
	for i in range(num):
		if len(hexes) > 0:
			x_0, y_0 = hexes[-1][3]
			x_0 += major_horiz_dist

		hexes.append(get_hex_coords(x_0, y_0, minor_horiz_dist, major_horiz_dist, minor_vert_dist))
	return hexes
	
def get_hex_latice(x_0, y_0, minor_horiz_dist, major_horiz_dist, minor_vert_dist):
	'''Return a list of lists of hex coords.'''
	
	# TODO move under class
	
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
	

def draw_hex(canvas, hex):
	'''Draw this hexagon object.'''
	
	# TODO move under class
	
	canvas.create_polygon(
		*CatanUtils.get_tkinter_coords(hex.get_vertices()), 
		fill=CatanRenderConstants.resource_color_map[hex.get_resource()], 
		outline="black"
	)
	
	draw_token(canvas, hex)
		
def draw_token(canvas, hex, draw_letter=False):
	'''Given the hex coords, draw the token.'''
	
	# TODO move under class
	
	hex_v = hex.get_vertices()
	
	# no need to draw token for desert tile
	if hex.get_resource() == "desert":
		return 
	
	padding = 5
	y_offset = 4 # how much above the center it should be
	
	center = ((hex_v[0][0] + hex_v[4][0]) / 2, (hex_v[1][1] + hex_v[-1][1]) / 2)
	
	adjusted_center = (
		hex_v[1][0] + CatanApp.major_horiz_dist / 2,
		center[1] - y_offset,
	)					
	
	canvas.create_oval(
		hex_v[1][0] + padding, 
		center[1] - CatanApp.major_horiz_dist / 2 + padding, 
		hex_v[2][0] - padding, 
		center[1] + CatanApp.major_horiz_dist / 2 - padding, 
		outline="black", 
		fill="white"
	)

	n = hex.get_number()
	c = "red" if n in [6, 8] else "black"
	
	canvas.create_text(adjusted_center, text=str(n), fill=c)
	
	if draw_letter:
		canvas.create_text((adjusted_center[0], adjusted_center[1] - 12), text=hex.get_token())
	
	draw_token_dots(canvas,  adjusted_center, n, c)
	
def draw_token_dots(canvas, pos, n, color):
	'''Draw the dots for the given hex'''
	
	# number of dots to draw
	num_dots = 6 - abs(7 - n)
	y_offset = 12 # to get below text
	pos = (pos[0], pos[1] + y_offset)
	x_offset = 8 # has to be even number
	
	if num_dots % 2:
		# create a central dot
		draw_token_dot(canvas, pos, color)
		
		# draw side dots
		for i in range(num_dots / 2):
			draw_token_dot(canvas, (pos[0] + (i + 1) * x_offset, pos[1]), color)
			draw_token_dot(canvas, (pos[0] - (i + 1) * x_offset, pos[1]), color)
	else:
		for i in range(num_dots / 2):
			draw_token_dot(canvas, (pos[0] + (i + .5) * x_offset, pos[1]), color)
			draw_token_dot(canvas, (pos[0] - (i + .5) * x_offset, pos[1]), color)
	
def draw_token_dot(canvas, pos, color):
	radius = 2
	
	canvas.create_oval(
		pos[0] - radius, 
		pos[1] - radius,
		pos[0] + radius,
		pos[1] + radius,
		fill=color,
		outline=""
	)
	
class CatanApp():
	'''The Catan App (for now).
	For now side distances are determined statically. Can dynamically allocate them at a later point.'''
	
	height = 550
	width = 750
	minor_horiz_dist = 30
	major_horiz_dist = 60
	minor_vert_dist = 50
	render_start = (200, minor_vert_dist + 20)
	
	settlement_radius = 20
	city_radius = 22
	
	players = ["red", "yellow", "blue", "green"]
	
	def _next_turn(self, decr=False):
		i=-1 if decr else 1
		self._turn = (self._turn + i) % 4
		
	def _get_turn(self):
		return self._turn
	
	def automate_setup(self):
		'''Create a random setup of the first two roads and settlements.'''
		
		# do all 8
		for i in range(8):
			c = self.players[self._turn]
			v = self._map.ai.get_random_settlement()
			self.add_settlement(None, v)
			road = self._map.ai.get_random_road_from_settlement(v)
			
			if not road:
				print "ERROR! Could not find a place to put a road"
			else:
				v1, v2 = road
			
			if v1[0] > v2[0]:
				v1, v2 = v2, v1 # switch places to correspond with the way roads are indexed
			
#			if (v1, v2) not in self._roads:
#				print "Tried to build road from {} to {}".format(v1, v2)
#				for k in self._roads.keys():
#					if k[0] == v1 or k[1] == v1:
#						print k
			
			self.add_road(None, v1, v2)
	
	def __init__(self):
		self._master = Tk()
	
		# frame
		frame = Frame(self._master)
		#frame.bind("<Key>", self.key_pressed)
		# keys to end game
		frame.bind("<Escape>", self.end)
		frame.bind("<Return>", self.end)
		frame.bind("<space>", self.end)
		frame.focus_set() # this is very important
		frame.grid()
		frame.master.title("Settlers of Catan: Whores and Wenches (custom expansion)")
		frame.pack()
		
		# keeps index of turn
		self._turn = 0
		
		# now to get a grid
		for i in range(6):
			frame.master.columnconfigure(i, weight=1)
		frame.master.rowconfigure(0, weight=1)

		frame1 = frame
		self._frame = frame

		# canvas
		w = Canvas(frame1, width=CatanApp.width, height=CatanApp.height)
		w.pack()
		
		# create the board
		self._map = MapGen()
		self._map.create_players(self.players)
		self._map.gen()
		self.set_vertices(self._map.get_map())
		self._map.prepare()
		
		self.draw_board(w)
		
		#self.play_game()
		self.draw_status_area()
		self._roll_var = StringVar()
		self._roll_button = Button(
			frame1, 
			text="End turn", 
			command=self.roll,
			state=DISABLED # initially hide it
		)
		self._roll_button.place(x=600, y=20)
		self._roll_button.pack()
		l = Label(frame1, textvar=self._roll_var)
		l.place(x=600, y=120)
		l.pack()
		
		self.automate_setup()
		
	def place_initial_settlements(self):
		'''Place the initial settlements.'''
		
		# step 1 - go forward through players, give no resources
		for p in range(4):
			pass
			# wait for user input
		
		# step 2 - go backward through players, give resources to adjacent tiles
		for p in range(3, -1, -1):
			pass
		
	def roll(self):
		'''End the previous turn, then roll the dice.'''
		
		# change turn
		self.change_status_turn()
		
		# roll the dice
		r1 = random.randint(1, 6)
		r2 = random.randint(1, 6)
		n = r1 + r2
		
		# display dice roll
		self._roll_var.set("Last roll: {}".format(n))
		
		# compute produced resources
		d = self._map.get_resources_produced(n)
		
		# update player hands on screen
		for c in self.players:
			self.update_hand(c)
			
	def update_hand(self, color):
		'''Update the hand displayed for player of the given color.'''
		
		self._canvas.itemconfigure(
			self._hands[color], 
			text=self._map.get_player(color).get_printable_hand()
		)
		
	def act_on_start_state(self):
		'''Set the state notification to the correct value.'''
		
		# set the note
		self.post_status_note()
		
		if self._state in ["first settlement placement", "second settlement placement"]:
			# disable roads
			for road in self._canvas.find_withtag("road"):
				self._canvas.itemconfigure(road, state=DISABLED)
			# disable city upgrades
			for s in self._canvas.find_withtag("settlement"):
				self._canvas.itemconfigure(s, state=DISABLED)
			for s in self._canvas.find_withtag("settlement_placeholder"):
				self._canvas.itemconfigure(s, state=NORMAL)
		elif self._state in ["first road placement", "second road placement"]:
			for s in self._canvas.find_withtag("settlement"):
				self._canvas.itemconfigure(s, state=DISABLED)
			for city in self._canvas.find_withtag("city"):
				self._canvas.itemconfigure(city, state=DISABLED)
		elif self._state == "gameplay":
			# disable all buildings
			#for b in self._canvas.find_withtag("building"):
			#	self._canvas.itemconfigure(b, state=DISABLED)
			# re-enable the roll button
			self._roll_button.config(state=NORMAL)
			#TODO for some reason the button is not being enabled
			print "Enabled roll button"
				
	def post_status_note(self, msg=None):
		if msg:
			t = msg
		else:
			if "settlement placement" in self._state:
				t = "Place a settlement"
			elif "road placement" in self._state:
				t = "Place a road"
			elif self._state == "gameplay":
				t = "Done with initial placements!"
			
		self._canvas.itemconfigure(self._note, text=t)
				
	def act_on_end_state(self):
		'''Perform state exit actions.'''
		
		if self._state in ["first settlement placement", "second settlement placement"]:
			for road in self._canvas.find_withtag("road"):
				self._canvas.itemconfigure(road, state=NORMAL)
			for city in self._canvas.find_withtag("city"):
				self._canvas.itemconfigure(city, state=NORMAL)
				
			if "second" in self._state:
				# note the turn hasn't changed
				c = self.players[self._turn]
				second_settlement =  self._map.get_player(c).get_settlement(1)
				self._map.produce(second_settlement)
				self.update_hand(c)
				
		elif self._state in ["first road placement", "second road placement"]:
			for s in self._canvas.find_withtag("settlement"):
				self._canvas.itemconfigure(s, state=NORMAL)
			for city in self._canvas.find_withtag("city"):
				self._canvas.itemconfigure(city, state=NORMAL)
		elif self._state == "gameplay":
			# re-enable all buildings
			for b in self._canvas.find_withtag("building"):
				self._canvas.itemconfigure(b, state=NORMAL)
		
		
	def draw_status_area(self):
		'''Draw whose turn it is in top-left corner.'''
		
		# this is where the turn is
		self._canvas.create_text(50, 30, text="Current turn:")
		self._status_rect = self._canvas.create_rectangle(
														50, 40, 80, 70, 
														fill=self.players[self._turn], 
														tag="status_rect"
														)
		
		# this is the notifications area
		self._note = self._canvas.create_text(600, 30, width=100)
		self._state = "first settlement placement"
		self.act_on_start_state()
		
		self._hands = {}
		
		# this is where the cards are
		for i, c in enumerate(self.players):
			self._canvas.create_rectangle(550, 100 * (i + 1), 580, 100 * (i + 1) + 30, fill=c, outline="black")
			self._hands[c] = self._canvas.create_text(670, 100 * (i + 1), text="", width=150, justify=RIGHT)
		
	def change_status_turn(self, decr=False):
		self._next_turn(decr)
		self._canvas.itemconfigure(self._status_rect, fill=self.players[self._turn])
		
	def draw_board(self, canvas):
		'''Now we draw the board...'''
		
		for row in self._map.get_map():
			for hex in row:
				draw_hex(canvas, hex)
				
		self._settlements = {}
		self._roads = {}
		self._canvas = canvas
		for r in self._map.get_roads():
			self.draw_road_placeholder(canvas, r[0], r[1])
			
		for v in self._map.get_nodes():
			self.draw_settlement_node(canvas, v)
		
	def get_roads(self):
		return self._road_set
	
	def _get_road_slope(self, v1, v2):
		'''Return float.'''
		
		return (v2[1] - v1[1]) * 1.0 / (v2[0] - v2[1])
	
	def _get_y_offset(self, v1, v2, x_offset):
		return self._get_road_slope(v1, v2) * x_offset
			
	def draw_road_placeholder(self, canvas, v1, v2):
		''' Create an invisible, clickable road placeholder between v1 and v2.
		When clicked, it will act like a button and trigger an add_road event here.'''
		
		tag = "road_placeholder_{}_{}_{}_{}".format(v1[0], v1[1], v2[0], v2[1])
		
		# make sure v1 is the left-most one
		if v1[0] > v2[0]:
			v1, v2 = v2, v1
			
		spacing = 10
		slope = self._get_road_slope(v1, v2)
		x_offsets = [10, v2[0] - v1[0] - 10] # 10 from left and 10 from right
		y_offsets = [self._get_y_offset(v1, v2, dx) for dx in x_offsets]
		
		if slope == 0:
			# have a horizontal offset but no vertical offset
			v = (
				(v1[0] + 5, v1[1] + 5),
				(v2[0] - 5, v1[1] + 5),
				(v2[0] - 5, v2[1] - 5),
				(v1[0] + 5, v2[1] - 5),
				)
		elif slope > 0: # this corresponds to neg. slope because of how Tkinter coords work
			
			v = (
				(v1[0] - 5, v1[1]),
				(v1[0] + 5, v1[1]),
				(v2[0] + 5, v2[1]),
				(v2[0] - 5, v2[1]),
				)
		else: # neg. slope in Tkinter == pos. slope in life
			v = (
				(v1[0] - 5, v1[1]),
				(v1[0] + 5, v1[1]),
				(v2[0] + 5, v2[1]),
				(v2[0] - 5, v2[1]),
				)
		
		self._roads[(v1, v2)] = canvas.create_polygon(
			*CatanUtils.get_tkinter_coords(v),
			tags=("road", tag, "building"),
			fill="", # transparent fill
		   	outline="" # no outline
		)
		
		f = lambda e: self.add_road(e, v1, v2)
		canvas.tag_bind(tag, "<Button>", func=f)
		
	def add_road(self, event, v1, v2):
		'''Build a road between two vertices in response to user click.'''
		
		color = self.players[self._turn]
		
		if self._map.add_road(v1, v2, color):
			print "Building {} road between {} and {}".format(color, v1, v2)
			tag = "road_placeholder_{}_{}_{}_{}".format(v1[0], v1[1], v2[0], v2[1])
			
			self._canvas.itemconfigure(self._roads[(v1, v2)], fill=color, outline="black")
			self._canvas.dtag(self._roads[(v1, v2)], tag)
			
			if self._state == "first road placement":
				if self._turn == 3:
					self.change_to_state("second settlement placement")
				else:
					self.change_status_turn()
					self.change_to_state("first settlement placement")
			elif self._state == "second road placement":
				if self._turn == 0:
					self.change_to_state("gameplay")
				else:
					self.change_status_turn(True)
					self.change_to_state("second settlement placement")
		else:
			msg = "Road must be attached to a settlement."
			print "Failed to build {} road between {} and {}.".format(color, v1, v2) + " " + msg
			self.post_status_note(msg)
			
	def cull_adjacent_settlement_nodes(self, canvas, v):
		'''Remove all settlement nodes which are adjacent to vertex v.'''
		
		# first, get adjacent vertices
		adjacent_v_set = self._map.get_adjacent_vertices(v)
		for adjacent_v in adjacent_v_set:
			s = self._settlements[adjacent_v] # these are ovals
			canvas.delete(s) # delete the oval
	
	def draw_settlement_node(self, canvas, v):
		'''Draw an invisible settlement node at the given vertex.
		When clicked, it will act like a button and trigger a draw_settlement event here.'''
		
		padding = CatanApp.settlement_radius / 2
		tag = "settlement_oval_{}_{}".format(*v)
		self._settlements[v] = canvas.create_oval(
		   v[0] - padding,
		   v[1] - padding,
		   v[0] + padding,
		   v[1] + padding, 
		   tags=("settlement", tag, "settlement_placeholder", "building"),
		   fill="", # transparent fill
		   outline="" # no outline
		)
		
		# curry the function
		f = lambda e: self.add_settlement(e, v)
		canvas.tag_bind(tag, "<Button>", func=f)
	
	def add_settlement(self, event, v):
		'''Add a settlement at the given vertex in response to user click.'''
		
		color = self.players[self._get_turn()]
		
		# reflect changes in the model
		result = self._map.add_settlement(v, color)
		if result:
			print "Building {} settlement at {}".format(color, v)
			
			# TODO change the color to reflect the color of the player
			# TODO use sprites instead of ovals
			# draw the settlement oval
			self._canvas.itemconfigure(self._settlements[v], fill=color)
			self._canvas.itemconfigure(self._settlements[v], outline="black")
			self._canvas.dtag(self._settlements[v], "settlement_placeholder")
			
			# create new callback
			f = lambda e: self.add_city(e, v, color)
			tag = "settlement_oval_{}_{}".format(*v)
			self._canvas.tag_bind(tag, "<Button>", func=f)
			
			# no need for this
			#self.cull_adjacent_settlement_nodes(self._canvas, v)
			
			if self._state == "first settlement placement":
				self.change_to_state("first road placement")
			elif self._state == "second settlement placement":
				self.change_to_state("second road placement")
		else:
			print "Failed to build {} settlement at {}".format(color, v)
			self.post_status_note("That building spot is too close to an existing settlement")
			
	def change_to_state(self, new_state):
		'''Move from state in self._state to new_state.'''
		
		self.act_on_end_state()
		self._state = new_state
		self.act_on_start_state()
		
	def add_city(self, event, v, color):
		'''Add a city on top of existing settlement in response to user click.'''
		
		print "Building {} city at {}".format(color, v)
		
		# destroy the oval
		self._canvas.delete(self._settlements[v])
		
		padding = CatanApp.city_radius / 2
		tag = "city_square_{}_{}".format(*v)
		
		self._settlements[v] = self._canvas.create_rectangle(
		   v[0] - padding,
		   v[1] - padding,
		   v[0] + padding,
		   v[1] + padding, 
		   tags=("city", tag, "building"),
		   fill=color, # transparent fill
		   outline="black" # no outline
		)
		
		# reflect changes in the model
		self._map.add_city(v, color)
		
	@staticmethod
	def set_vertices(map):
		''' match the board with the generated map 
		'''
		
		# latice AKA board
		# TODO maybe calculate vertices rather than generating them all at once
		hex_coord_latice = get_hex_latice(
			CatanApp.render_start[0], 
			CatanApp.render_start[1], 
			CatanApp.minor_horiz_dist, 
			CatanApp.major_horiz_dist, 
			CatanApp.minor_vert_dist
		)
		
		for row_i, row in enumerate(map):
			for col_i, col in enumerate(row):
				col.set_vertices(hex_coord_latice[row_i][col_i])
		
	def key_pressed(self, event):
		print repr(event.char)

	def end(self, event):
		print "exit event captured"
		self._master.destroy()
		#sys_exit(0)
	
	def run(self):
		#TODO and the window is stuck at the front >_<  
		self._master.attributes("-topmost", 1) # this raises window to front
		
		#TODO focus is still not on top window
		
		self._master.mainloop()
		

def render_map():
	'''Draw the map.'''
	
	app = CatanApp()
	app.run()

if __name__ == "__main__":
	render_map()
	pass

	
	

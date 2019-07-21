#############################
#	Written by Daniel Kats	#
#	December 25, 2012		#
#############################

'''
This file is is mainly concerned with:
	- the 'view' aspect (i.e. representation of board on screen)
	- the 'control' aspect (i.e. responding to user-caused events such as button clicks)

TODO break up the view and control portions
'''

#############
#	IMPORTS	#
#############

from tkinter import RIGHT, DISABLED, W, HIDDEN, NORMAL, Tk, Frame, Button, StringVar, S, Label, Canvas
from catan_gen import CatanConstants, CatanRenderConstants
from game_engine import Game, DevelopmentCardError, SettlementPlacementError, CityUpgradeError, RoadPlacementError, GameState
from utils import CatanUtils
from catan_types import Vertex
import math
import logging
from ai.smart_placement_ai import SmartPlacementAI
from typing import Dict


logger = logging.getLogger(__name__)


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


def get_hex_lattice(x_0, y_0, minor_horiz_dist, major_horiz_dist, minor_vert_dist):
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


def draw_hex(canvas, hex, row, col):
	'''Draw this hexagon object.'''

	canvas.create_polygon(
		*CatanUtils.get_tkinter_coords(hex.get_vertices()),
		fill=CatanRenderConstants.resource_color_map[hex.get_resource()],
		outline="black",
		tags=("hex", "hex_{}_{}".format(row, col))
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
	num_dots = CatanUtils.get_num_token_dots(n)
	y_offset = 12 # to get below text
	pos = (pos[0], pos[1] + y_offset)
	x_offset = 8 # has to be even number

	if num_dots % 2:
		# create a central dot
		draw_token_dot(canvas, pos, color)

		# draw side dots
		for i in range(math.floor(num_dots / 2)):
			draw_token_dot(canvas, (pos[0] + (i + 1) * x_offset, pos[1]), color)
			draw_token_dot(canvas, (pos[0] - (i + 1) * x_offset, pos[1]), color)
	else:
		for i in range(math.floor(num_dots / 2)):
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
	width = 900
	minor_horiz_dist = 30
	major_horiz_dist = 60
	minor_vert_dist = 50
	render_start = (200, minor_vert_dist + 20)

	settlement_radius = 20
	city_radius = 22

	robber_height = 40
	robber_width = 40

	players = ["red", "gold2", "blue", "green"]

	def draw_robber(self):
		# the robber has an associated hex
		center = self._map.get_robber_hex().get_center()
		self._robber_sprite = self._canvas.create_oval(
			center[0] - self.robber_width / 2,
			center[1] - self.robber_height / 2,
			center[0] + self.robber_width / 2,
			center[1] + self.robber_height / 2,
			tag="robber",
			fill="black",
			activefill="yellow",
			state=DISABLED
		)

	def grab_robber(self, event):
		self._grab_item = {
			"x" : event.x,
			"y" : event.y,
			"item" : self._canvas.find_withtag("robber")
		}

	def move_robber(self, event):
		self._canvas.move(
			self._grab_item["item"],
			event.x - self._grab_item["x"],
			event.y - self._grab_item["y"]
		)
		self._grab_item["x"] = event.x
		self._grab_item["y"] = event.y

	def release_robber(self, event):
		# get the closest hex...
		items = self._canvas.find_overlapping(event.x - 15, event.y - 15, event.x + 15, event.y + 15)

		for item in items:
			tags = self._canvas.gettags(item)
			if "hex" in tags:
				coord = tuple([int(i) for i in tags[1].replace("hex_", "").split("_")])

				if self._map.set_robber_hex(coord[0], coord[1]):
					center = self._map.get_robber_hex().get_center()
					self._canvas.move(
						self._robber_sprite,
						center[0] - self._grab_item["x"],
						center[1] - self._grab_item["y"]
					)

					# TODO - allow me to re-pickup the robber and move it again
					self.enable_stealing()
				else:
					print("ROBBER FAIL")
					self.move_robber_to_hex(self._map.get_robber_hex())
					return

	def enable_stealing(self):
		'''Enable stealing by the current player from all players adjoining the robber hex.'''

		# only allow stealing from players who are adjacent to that hex
		player_list = self._map.get_players_on_robber_hex()

		if len(player_list) == 0:
			# don't steal from anybody
			self.change_to_state("gameplay")
		elif len(player_list) == 1:
			# don't go through trouble of selection here, since there is only 1 choice
			self.steal_from_player(player_list[0])
			self.change_to_state("gameplay")
		else:
			for c in player_list:
				t = "player_hand_rect_%s" % c
				self._canvas.itemconfigure(self._canvas.find_withtag(t)[0], state=NORMAL)

	def _next_turn(self):
		self._map.next_turn()
		self._turn = self._map.get_turn()

	def _get_turn(self):
		return self._turn

	def move_robber_to_hex(self, destination_hex):
		'''Move robber to the given hex. Here, hex is the Hex object.'''

		new_pos = destination_hex.get_center()
		old_pos = self._canvas.coords(self._robber_sprite)
		old_pos_c = ((old_pos[0] + old_pos[2]) / 2, (old_pos[1] + old_pos[3]) / 2)
		self._canvas.move(self._robber_sprite, new_pos[0] - old_pos_c[0], new_pos[1] - old_pos_c[1])

	def automate_robber(self):
		'''Automate the robber completely.'''

		self.automate_robber_movement()
		self.automate_robber_steal_picking()
		#self.change_to_state("gameplay")

	def automate_robber_steal_picking(self):
		'''Automate the process of picking a person to steal from, once robber has been placed.'''

		ai = self._ais[self._map.get_current_color()]
		color = ai.get_robber_pick(self._map)
		self.steal_from_player(color)

	def automate_robber_movement(self):
		'''Choose a place to put the robber.'''

		color = self.players[self._turn]
		ai = self._ais[color]
		row, col = ai.get_robber_placement(self._map, color)
		#destination_hex_sprite = self._canvas.find_withtag("hex_{}_{}".format(row, col))
		model_hex = self._map._board[row][col]

		if self._map.set_robber_hex(row, col):
			self.move_robber_to_hex(model_hex)
		else:
			print("AI picked same hex to put robber, skipping stealing...")
			#self.move_robber_to_hex(self._map.get_robber_hex())

	def automate_placement(self):
		'''Create a random placement of the first two roads and settlements for each player.'''

		while self._map.get_state() == GameState.INITIAL_PLACEMENT:
			ai = self._ais[self._map.get_current_color()]
			v = ai.get_settlement_placement(self._map)
			assert v is not None
			self.add_settlement(None, v, initial_placement=True)
			road = ai.get_road_placement(self._map, v)
			assert road[0] == v or road[1] == v
			self.add_road(None, road[0], road[1], initial_placement=True)
			self.change_status_turn()

		self.change_to_state("gameplay")
		self.roll(change_turn=False)

	def __init__(self):
		self._master = Tk()

		# frame
		frame = Frame(self._master)
		#frame.bind("<Key>", self.key_pressed)
		# keys to end game
		frame.bind("<Escape>", self.end)
		frame.bind("<Return>", self.roll)
		frame.bind("<space>", self.roll)
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
		hex_coord_lattice = CatanApp.get_hex_coord_lattice()
		self._map = Game(
			starting_color=self.players[self._turn],
			colors=self.players,
			hex_coord_lattice=hex_coord_lattice
		)
		self.set_vertices(self._map.get_map())

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
		#self._roll_button.place(x=600, y=20)
		#self._roll_button.pack()

		self._canvas.create_window(60, self.height + 10, window=self._roll_button, anchor=S)

		l = Label(frame1, textvar=self._roll_var)
		l.place(x=600, y=120)
		l.pack()

		self.create_build_buttons()

		self._canvas.create_window(170, self.height + 10, window=self._build_buttons["settlement"], anchor=S)

		self.draw_robber()
		# bind events to the robber
		self._canvas.tag_bind("robber", "<ButtonPress-1>", self.grab_robber)
		self._canvas.tag_bind("robber", "<B1-Motion>", self.move_robber)
		self._canvas.tag_bind("robber", "<ButtonRelease-1>", self.release_robber)

		self._ais = {}  # type: Dict[str, SmartPlacementAI]
		for color in self.players:
			self._ais[color] = SmartPlacementAI(color, self._map)

		self.automate_placement()

	def play_dev_card(self):
		raise NotImplementedError()

	def buy_development_card(self):
		'''User-triggered action to buy a development card.'''

		color = self.players[self._turn]
		try:
			card = self._map.get_development_card(color)
			self.post_status_note("Successfully bought development card")
			self.update_hand(color)
			print("{} bought development card '{}'".format(color, card))
			self.update_dev_cards(color)
			self.update_vp(color)
		except DevelopmentCardError as e:
			self.post_status_note(str(e), True)

	def create_build_buttons(self):
		'''Create buttons to build various structures.'''

		self._build_buttons = {}

		for type in ["road", "settlement", "city"]:
			self.create_build_button(type)

		self._build_buttons["dev_card"] = Button(
			self._frame,
			text="Buy development card",
			state=DISABLED,
			command=self.buy_development_card
		)

		self._build_buttons["dev_card"].pack()

		f = lambda: self.change_to_state("gameplay")

		self._cancel_building_button = Button(
			self._frame,
			text="Cancel building",
			state=DISABLED,
			command=f
		)
		self._cancel_building_button.pack()

	def enable_building(self, type):
		'''Enable building of buildings of certain type.
		NOTE: player has not been charged by this point.'''

		color = self.players[self._turn]
		p = self._map.get_player(color)
		if p.can_deduct_resources(CatanConstants.building_costs[type]):
			if type == "city":
				for item in self._canvas.find_withtag("settlement"):
					self._canvas.itemconfigure(item, state=NORMAL)
				for item in self._canvas.find_withtag("settlement_placeholder"):
					self._canvas.itemconfigure(item, state=DISABLED)
			else:
				for item in self._canvas.find_withtag(type + "_placeholder"):
					self._canvas.itemconfigure(item, state=NORMAL)

			self.change_to_state("place additional building")
		else:
			self.post_status_note("{} does not have enough resources to build a {}".format(color, type), True)

	def create_build_button(self, type):
		'''Create button to build given structure.'''

		f = lambda: self.enable_building(type)

		self._build_buttons[type] = Button(
			self._frame,
			text="Build {}".format(type),
			command=f,
			state=DISABLED
		)

		self._build_buttons[type].pack()

	def check_game_end(self) -> bool:
		for color in self.players:
			vp = self._map.get_player_vp(color)
			if vp >= 10:
				return True
		return False

	def process_game_end(self):
		# get the winner
		# winning_player = None
		winning_color = None
		for color in self.players:
			vp = self._map.get_player_vp(color)
			if vp >= 10:
				# winning_player = self._map.get_player(color)
				winning_color = color
				break
		self.post_status_note(
			f"Game over! Player {winning_color} wins!"
		)

	def roll(self, change_turn=True):
		'''End the previous turn, then roll the dice.'''

		if change_turn and self.check_game_end():
			self.process_game_end()
			return

		if change_turn:
			self.change_status_turn()

		n = self._map.roll_dice()

		# display dice roll
		self._roll_var.set("Last roll: {}".format(n))
		self.post_status_note("Rolled %d" % n)

		if n == 7:
			for color in self.players:
				ai = self._ais[color]
				player = self._map.get_player(color)
				# AI responsible for discarding cards
				cards = ai.robber_discard(self._map, color)
				if cards != []:
					logger.debug("%s discarded %s due to robber, now have %d cards",
								color, cards, player.get_num_resources())
				assert player.get_num_resources() <= 7

			self.change_to_state("move robber")

			#for i in range(4):
			#	c = self.players[self._turn]
			#	# this player must discard <x> cards
			#	if c in discard_map:
			#		self.post_status_note("{} must discard {} cards".format(c.title(), discard_map[c]), True)
		else:
			# compute produced resources
			self._map.produce_resources_from_roll(n)

			# update player hands on screen
			for c in self.players:
				self.update_hand(c)

	def update_hand(self, color):
		'''Update the hand displayed for player of the given color.'''

		self._canvas.itemconfigure(
			self._hands[color],
			text=self._map.get_player(color).get_printable_hand().replace(",", "\n")
		)

	def update_dev_cards(self, color):
		'''Update development card display in GUI for player of given color.'''

		item = self._canvas.find_withtag("dev_area_section_%s" % color)
		self._canvas.itemconfigure(
			item,
			text=self._map.get_player(color).get_printable_dev_cards().replace(",", "\n")
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
			for b in self._canvas.find_withtag("building"):
				self._canvas.itemconfigure(b, state=DISABLED)
			# re-enable the roll button
			self._roll_button.config(state=NORMAL)
			for button in self._build_buttons.values():
				button.config(state=NORMAL)
		elif self._state == "choose building":
			# hide the hand while building
			for item in self._canvas.find_withtag("hand_area_section"):
				self._canvas.itemconfigure(item, state=HIDDEN)

			for item in self._canvas.find_withtag("building_selection"):
				self._canvas.itemconfigure(item, state=NORMAL)

		elif self._state == "place additional building":
			# disable the buttons
			self._roll_button.config(state=DISABLED)
			for b in self._build_buttons.values():
				b.config(state=DISABLED)
			self._cancel_building_button.config(state=NORMAL)

		elif self._state == "move robber":
			self._roll_button.config(state=DISABLED)
			self._build_buttons["settlement"].config(state=DISABLED)
			for s in self._canvas.find_withtag("building"):
				self._canvas.itemconfigure(s, state=DISABLED)
			self._canvas.itemconfigure(self._robber_sprite, state=NORMAL)

			# TODO for now
			self.automate_robber()
			#self.change_to_state("gameplay")

		elif self._state == "choose player":
			# enable the hand rectangles
			#for rect in self._canvas.find_withtag("player_hand_rect"):
			#	self._canvas.itemconfigure(rect, state=NORMAL)
			self.enable_stealing()

			# disable basically everything else
			for s in self._canvas.find_withtag("building"):
				self._canvas.itemconfigure(s, state=DISABLED)
			self._roll_button.config(state=DISABLED)
			self._build_buttons["settlement"].config(state=DISABLED)

	def post_status_note(self, msg=None, error=False):
		c = "red" if error else "black"

		if msg:
			t = msg
		else:
			if "settlement placement" in self._state:
				t = "Place a settlement"
			elif "road placement" in self._state:
				t = "Place a road"
			elif self._state == "gameplay":
			#	t = "Done with initial placements!"
				t = None
			elif self._state == "move robber":
				t = "Move the robber"
			elif self._state == "choose player":
				t = "Choose a player to steal from"
			elif self._state == "choose building":
				t = "Choose a building to build"
			elif self._state == "place additional building":
				t = "Place the building you just bought"

		if t is not None:
			self._canvas.itemconfigure(self._note, text=t, fill=c)

	def act_on_end_state(self):
		'''Perform state exit actions.'''

		if self._state == "gameplay":
			# re-enable all buildings
			for b in self._canvas.find_withtag("building"):
				self._canvas.itemconfigure(b, state=NORMAL)
			self._roll_button.config(state=DISABLED)
		elif self._state == "move robber":
			self._roll_button.config(state=NORMAL)
			self._build_buttons["settlement"].config(state=NORMAL)
			for s in self._canvas.find_withtag("building"):
				self._canvas.itemconfigure(s, state=DISABLED)
			# this is the main part
			self._canvas.itemconfigure(self._robber_sprite, state=DISABLED)
		elif self._state == "choose player":
			for rect in self._canvas.find_withtag("player_hand_rect"):
				self._canvas.itemconfigure(rect, state=DISABLED)
			# the usual stuff will be enabled when gameplay is resumed
		elif self._state == "choose building":
			# hide the hand while building
			for item in self._canvas.find_withtag("hand_area_section"):
				self._canvas.itemconfigure(item, state=NORMAL)

			for item in self._canvas.find_withtag("building_selection"):
				self._canvas.itemconfigure(item, state=HIDDEN)
		elif self._state == "place additional building":
			# re-enable the buttons
			self._roll_button.config(state=NORMAL)
			for b in self._build_buttons.values():
				b.config(state=NORMAL)

			# disable the buildings
			for s in self._canvas.find_withtag("building"):
				self._canvas.itemconfigure(s, state=DISABLED)
			self._cancel_building_button.config(state=DISABLED)

			# update hand
			self.update_hand(self.players[self._turn])

			# post that the building is good
			self.post_status_note("Successfully built the building!", False)

	def draw_build_menu(self):
		'''Draw the build menu.'''

		x = 550
		y_start = 100
		y_incr = 70
		build_list = ["settlement", "city", "road"]

		for i in range(len(build_list)):
			l = Label(self._canvas, text=build_list[i], anchor=W, font=("Helvetica", 16))

			self._canvas.create_window(
				x,
				y_start + i * y_incr,
				window=l,
				state=HIDDEN,
				tag="building_selection",
				anchor=W
			)

			# TODO - create sprite for it

			#b = self._canvas.bbox(w)
			#self._canvas.itemconfigure(b, outline="black")

	def draw_status_area(self):
		'''Draw whose turn it is in top-left corner.
		Also draw player hands'''

		self.draw_build_menu()

		# this is where the turn is
		self._canvas.create_text(50, 30, text="Current turn:")
		self._status_rect = self._canvas.create_rectangle(
			50, 40, 80, 70,
			fill=self.players[self._turn],
			tag="status_rect"
		)

		# this is the notifications area
		self._note = self._canvas.create_text(580, 30, width=180)
		self._state = "first settlement placement"
		self.act_on_start_state()

		self.draw_hand_area()

	def update_vp(self, color):
		'''Update the victory points for a player of the given color.'''

		item = self._canvas.find_withtag("player_hand_rect_%s_text" % color)
		self._canvas.itemconfigure(item, text=str(self._map.get_player_vp(color)))

	def draw_hand_area_section(self, color: str, i: int):
		'''Draw the section of the hand area for player of given color'''
		f = lambda event : self.steal_from_player(color)
		t = "player_hand_rect_%s" % color

		self._canvas.create_rectangle(
			550,
			120 * (i + 1) - 20,
			580,
			120 * (i + 1) + 10,
			fill=color,
			outline="black",
			tag=("player_hand_rect", t, "hand_area_section"),
			state=DISABLED,
			activeoutline="gold4",
		)

		self._canvas.create_text(
			565,
			120 * (i + 1) - 5,
			text="0",
			tag=t + "_text",
			font=("Helvetica", 14),
			fill="white"
		)

		self._hands[color] = self._canvas.create_text(
			670,
			120 * (i + 1),
			text="",
			width=150,
			justify=RIGHT,
			tag="hand_area_section"
		)
		self._canvas.tag_bind(t, "<Button>", f)

		self._canvas.create_text(
			770,
			120 * (i + 1),
			text="NO DEV CARDS",
			width = 150,
			justify=RIGHT,
			tag="dev_area_section_%s" % color
		)

		# create a box around the whole thing
		self._canvas.create_rectangle(
			530,
			120 * (i + 1) - 50,
			850,
			120 * (i + 1) + 50,
			fill="",
			outline=color,
			tag="hand_area_section",
			width=1.5
		)

	def draw_hand_area(self):
		'''Draw the area where the hands for the players are displayed.'''

		self._hands = {}

		# this is where the cards are
		for i, color in enumerate(self.players):
			self.draw_hand_area_section(color, i)

		# and a box around everything
		self._canvas.create_rectangle(
			525,
			65,
			855,
			535,
			fill="",
			outline="black",
			width=1.5,
			dash=(2, 4)
		)

	def steal_from_player(self, from_player: str):
		'''Steal from player of given player color.
		Called by selecting player color in robber motion.'''

		to_player = self.players[self._turn]
		self._map.robber_steal(from_player, to_player)
		self.update_hand(from_player)
		self.update_hand(to_player)
		self.post_status_note("Stole from {}".format(from_player))
		self.change_to_state("gameplay")

	def change_status_turn(self):
		# '''Change turn
		self._next_turn()
		self._canvas.itemconfigure(self._status_rect, fill=self.players[self._turn])

	def draw_board(self, canvas):
		'''Draw the catan board'''

		for row_i, row in enumerate(self._map.get_map()):
			for col, hex in enumerate(row):
				draw_hex(canvas, hex, row_i, col)

		self._settlements = {}
		self._roads = {}
		self._canvas = canvas
		for road in self._map.get_roads():
			self.draw_road_placeholder(canvas, road[0], road[1])

		for v in self._map.get_nodes():
			self.draw_settlement_node(canvas, v)

	def _get_road_slope(self, v1, v2):
		'''Return float.'''

		return (v2[1] - v1[1]) * 1.0 / (v2[0] - v2[1])

	def _get_y_offset(self, v1, v2, x_offset):
		return self._get_road_slope(v1, v2) * x_offset

	def draw_road_placeholder(self, canvas, v1: Vertex, v2: Vertex):
		''' Create an invisible, clickable road placeholder between v1 and v2.
		When clicked, it will act like a button and trigger an add_road event here.'''

		tag = "road_placeholder_{}_{}_{}_{}".format(v1[0], v1[1], v2[0], v2[1])

		# make sure v1 is the left-most one
		v1, v2 = self._map._normalize_road(v1, v2)

		# spacing = 10
		slope = self._get_road_slope(v1, v2)
		# x_offsets = [10, v2[0] - v1[0] - 10] # 10 from left and 10 from right
		# y_offsets = [self._get_y_offset(v1, v2, dx) for dx in x_offsets]

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
			tags=("road", tag, "building", "road_placeholder"),
			fill="", # transparent fill
		   	outline="" # no outline
		)

		f = lambda e: self.add_road(e, v1, v2)
		canvas.tag_bind(tag, "<Button>", func=f)

	def add_road(self, event, v1: Vertex, v2: Vertex, initial_placement: bool = False):
		'''Build a road between two vertices in response to user click.'''

		color = self._map.get_current_color()
		v1, v2 = self._map._normalize_road(v1, v2)

		# here we update the model
		try:
			if initial_placement:
				logger.info("Placing {} road between {} and {}...".format(color, v1, v2))
			else:
				logger.info("Building {} road between {} and {}...".format(color, v1, v2))
			self._map.add_road(v1, v2, color, initial_placement=initial_placement)
			tag = "road_placeholder_{}_{}_{}_{}".format(v1[0], v1[1], v2[0], v2[1])

			self._canvas.itemconfigure(self._roads[(v1, v2)], fill=color, outline="black")
			self._canvas.dtag(self._roads[(v1, v2)], tag)
			self._canvas.dtag(self._roads[(v1, v2)], "road_placeholder")

			self.update_vp(color)

			self.change_to_state("gameplay")
		except RoadPlacementError as e:
			msg = str(e)
			logger.error(e)
			self.post_status_note(msg, error=True)

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

	def add_settlement(self, event, v: Vertex, initial_placement: bool = False):
		'''Add a settlement at the given vertex in response to user click.'''

		color = self._map.get_current_color()

		# reflect changes in the model
		try:
			if initial_placement:
				logger.info("Placing %s settlement at %s...", color, v)
			else:
				logger.info("Building %s settlement at %s...", color, v)
			self._map.add_settlement(v, color, initial_placement=initial_placement)

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

			self.update_vp(color)

			self.change_to_state("gameplay")
		except SettlementPlacementError as e:
			logger.error("Failed to build %s settlement at %s", color, v)
			logger.error(str(e))
			self.post_status_note(str(e), error=True)

	def change_to_state(self, new_state):
		'''Move from state in self._state to new_state.'''

		self.act_on_end_state()
		self._state = new_state
		self.act_on_start_state()

	def add_city(self, event, v, color):
		'''Add a city on top of existing settlement in response to user click.'''

		try:
			self._map.add_city(v, color)
			print("Building {} city at {}".format(color, v))

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
			self.update_vp(color)
			self.change_to_state("gameplay")
		except CityUpgradeError as e:
			logger.error("Failed to upgrade %s settlement at %s", color, v)
			logger.error(str(e))
			self.post_status_note(str(e), error=True)

	@staticmethod
	def get_hex_coord_lattice():
		hex_coord_lattice = get_hex_lattice(
			CatanApp.render_start[0],
			CatanApp.render_start[1],
			CatanApp.minor_horiz_dist,
			CatanApp.major_horiz_dist,
			CatanApp.minor_vert_dist
		)
		return hex_coord_lattice

	@staticmethod
	def set_vertices(map):
		''' match the board with the generated map
		'''

		# lattice AKA board
		# TODO maybe calculate vertices rather than generating them all at once
		hex_coord_lattice = get_hex_lattice(
			CatanApp.render_start[0],
			CatanApp.render_start[1],
			CatanApp.minor_horiz_dist,
			CatanApp.major_horiz_dist,
			CatanApp.minor_vert_dist
		)

		for row_i, row in enumerate(map):
			for col_i, col in enumerate(row):
				col.set_vertices(hex_coord_lattice[row_i][col_i])

	def key_pressed(self, event):
		print(repr(event.char))

	def end(self, event):
		print("exit event captured")
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
	import coloredlogs
	logging.basicConfig(level=logging.DEBUG)
	coloredlogs.install(level=logging.DEBUG)
	render_map()

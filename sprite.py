'''
Draws a settlement, with the ability to rescale it.
Can similarly port to a city sprite, road sprite, etc.
Maybe sprites would be easier than drawing everything every time...
'''

#################
#	IMPORTS		#
#################

from tkinter import *
from utils import *

# constants for settlement
settlement_constants = {
	"front_rect_height" : 100,
	"front_width" : 100,
	"front_tri_height" : 50,
	"side_y_offset" : 50,
	"side_height" : 80,
	"side_width" : 50,
	"roof_x_offset" : 10,
	"roof_y_offset" : 30,
	"roof_height" : 45,
}

def scale_constants(constants, new_height):
	ratio = new_height * 1.0 / (constants["front_rect_height"] + constants["front_tri_height"])
	d = {}

	for k, v in constants.items():
		d[k] = int(v * ratio)

	return d

def print_dict(d):
	for k, v in d.items():
		print("{} ==> {}".format(k, v))

def get_front_face_coords(constants):
	'''Return tuple of tuples in form ( (x1, y1), ..., (xn, yn))
	These tuples are coordinates of the front face of the settlement.'''

	return (
		(0, 0),
		(0, constants["front_rect_height"]),
		(constants["front_width"] / 2, constants["front_rect_height"] + constants["front_tri_height"]),
		(constants["front_width"], constants["front_rect_height"]),
		(constants["front_width"], 0),
	)

def get_side_roof_coords(offset, constants, front):
	return (
		front[3], # bottom-left
		(front[3][0] + constants["side_width"], constants["front_rect_height"] + constants["roof_y_offset"]), # bottom-right
		(constants["front_width"] + constants["roof_x_offset"], constants["front_rect_height"] + constants["roof_y_offset"] + constants["roof_height"]), # top-right
		front[2], # top-left
	)

def get_side_coords(offset, constants, front):
	return (
		front[-1],
		(front[-1][0] + constants["side_width"], front[-1][1] + constants["side_y_offset"]),
		(front[-1][0] + constants["side_width"], front[-1][1] + constants["side_y_offset"] + constants["side_height"]),
		front[3]
	)

def draw_settlement(canvas, offset, top, constants):
	'''Draw the settlement given certain constants.'''

	front = get_front_face_coords(offset, constants)

	canvas.create_polygon(
		*to_tkinter_coords(front, top),
		fill="blue",
		outline="black"
	)

	canvas.create_polygon(
		*to_tkinter_coords(get_side_roof_coords(offset, constants, front), top),
		fill="blue",
		outline="black"
	)

	canvas.create_polygon(
		*to_tkinter_coords(get_side_coords(offset, constants, front), top),
		fill="blue",
		outline="black"
	)

def get_city_front_face_coords(constants):
	return (
		(0, 0), #bottom-left
		(0, 100), # top-left
		(200, 100), #top-right
		(200, 0), #bottom-right
	)

def get_short_tower_coords(constants, face):
	return (
		(face[2][0] - 70, face[2][1]), #bottom-left
		(face[2][0] - 70, face[2][1] + 50), # tower top-left
		(face[2][0] - 35, face[2][1] + 70), # peak
		(face[2][0], face[2][1] + 50), # tower top-right
		(face[2][0], face[2][1]), #bottom-right
	)

def get_tall_tower_coords(constants, face):
	return (
		face[1], #bottom-left
		(face[1][0], face[1][1] + 80), # tower top-left
		(face[1][0] + 30, face[1][1] + 120), # peak
		(face[1][0] + 60, face[1][1] + 80), # tower top-right
		(face[1][0] + 60, face[1][1]), #bottom-right
	)


def draw_city(canvas, offset, top, constants):
	front = get_city_front_face_coords(constants)

	canvas.create_polygon(
		*to_tkinter_coords(front, top, offset),
		fill = "red",
		outline = "black"
	)

	canvas.create_polygon(
		*to_tkinter_coords(get_short_tower_coords(constants, front), top, offset),
		fill = "red",
		outline = "black"
	)

	canvas.create_polygon(
		*to_tkinter_coords(get_tall_tower_coords(constants, front), top, offset),
		fill = "red",
		outline = "black"
	)

def rescale(canvas, offset, top, v):
	canvas.delete(ALL)
	d = scale_constants(settlement_constants, int(v))
	draw_settlement(canvas, (offset, offset), top, d)

if __name__ == "__main__":
	offset = 50
	top = 300
	d = {}

	# create a root
	master = Tk()

	# create the canvas
	w = Canvas(master, width=300, height=top)
	w.pack()

	# curry the rescale function
	#f = lambda v : rescale(w, offset, top, v)

	#s = Scale(master, from_=0, to=100, orient=HORIZONTAL,command=f)
	#s.pack()

	#draw_settlement(w, (offset, offset), top, settlement_constants)
	draw_city(w, (offset, offset), top, d)

	# start main loop
	master.mainloop()



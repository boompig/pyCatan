#############################
#	Written by Daniel Kats	#
#	December 25, 2012		#
#############################

#################
#	IMPORTS		#
#################
from catan_gen import CatanConstants

class Hex():
	'''
	This is a hex-tile on the catan board.
	Add methods as needed.
	'''

	def __init__(self, resource):
		self._r = resource
		self._t = None
		self._n = None
		self._v = []

	def get_resource(self):
		return self._r

	def set_vertices(self, vertices):
		self._v = vertices

	def get_vertices(self):
		return self._v

	def set_token(self, t):
		self._t = t
		self._n = CatanConstants.token_map[self._t]
		
	def get_number(self):
		return self._n

	def get_token(self):
		if self._t is None:
			return "DESERT"
		else:
			return self._t

	def get_vertex(self, index):
		if isinstance(index, int):
			return self._v[index]
		elif isinstance(index, str):
			if index == "left":
				return self._v[0]
			elif index == "right":
				return self._v[3]
			
	def get_top(self):
		return self._v[1][1]

	def get_bottom(self):
		return self._v[-1][1]

	def get_left(self):
		return self._v[0][0]

	def get_right(self):
		return self._v[3][0]

def print_bar():
	print "=" * 40

if __name__ == "__main__":
	v = (
		(0, 1),
		(1, 2),
		(2, 2),
		(3, 1),
		(2, 0),
		(1, 0),
	)

	r = "wood"
	t = 9

	h = Hex(r, t, v)

	print_bar()
	print h.get_vertex("right")
	print h.get_vertex("left")

	print_bar()
	print h.get_top()
	print h.get_bottom()
	print h.get_left()
	print h.get_right()

	print_bar()
	print h.get_token()

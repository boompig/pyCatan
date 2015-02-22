#############################
#	Written by Daniel Kats	#
#	August 1, 2012			#
#############################

from resource import Resource
from buildings import House

'''
Possible improvements:
- remove resource object if it looks unused
- remove token object if it looks unused
'''

class Tile(object):
	'''A single tile (placed or unplaced) in game of Catan.'''
	
	def __init__(self, resource):
		'''Create a new tile.'''
	
		# resource (type)
		self.__r = resource
		
		# token (letter and number)
		self.__t = None
		
		# set of vertices
		self.__v = []
		
		# list of attached houses
		self.__h = []
		
		# list of vertices that has a house (indices)
		self.__b = []
		
	def resource(self):
		'''Return resource object.'''
	
		return self.__r
		
	def name(self):
		'''Return the name of the resource object.'''
	
		return self.resource().name()

	def place(self, token):
		'''Place the tile by assigning it a token.'''
	
		self.__t = token
		
	def number(self):
		'''Return the number associated with this tile.
		Only makes sense after the tile has been placed.'''
		
		return None if self.__t is None else self.__t.number()
		
	def letter(self):
		'''Return the letter associated with this tile.
		Only makes sense after the tile has been placed.'''
		
		return None if self.__t is None else self.__t.letter()
		
	def set_vertices(self, v):
		'''Set the vertices for this tile. Used for settlement lookup, among other things.
		LIST of vertices.'''
		
		self.__v = list(v)
		
	def get_buildable_vertices(self):
		'''Set vertices at which it is OK to build a house (i.e. they are unoccupied).'''
		
		v = set(range(6))
		
		for v_i in self.__b:
			v -= set([v_i, (v_i + 1) % 6, (v_i + 5) % 6])
			
		return set([self.__v[i] for i in v])
		
	def get_vertices(self):
		'''Get back the vertices.'''
		
		return self.__v
		
	def add_house(self, h, vertex):
		'''Add the given house to this tile, at the given vertex.'''
		
		self.__h.append(h)
		self.__b.append(self.__v.index(vertex))
		
	def rolled(self):
		'''Return how much of this resource to give out to each player.
		Dictionary mapping player (color) to list of resource cards.
		Not all players included (include only relevant)'''
		
		d = {}
		
		for house in self.__h:
			if house.player() not in d: d[house.player()] = []
			
			d[house.player()].extend([self.name()] * house.points())
			
		return d
		
	def print_tile(self):
		'''For debugging.'''
		
		print "resource: {}".format(self.__r.name())
		print "vertices: {}".format(self.__v)
		
		if len(self.__h) > 0:
			print "houses:"
			
			for i in range(len(self.__h)):
				print "\t{} at vertex index {}".format(self.__h[i], self.__b[i])
		
if __name__ == "__main__":
	# simple test of tile methods
	t = Tile(Resource("wheat"))
	
	v = [(0, 0), (4, 3), (4, 5), (0, 8), (-4, 5), (-4, 3)]
	t.set_vertices(v)

	h = House("purple", v[0])
	t.add_house(h, v[0])
	
	# add a city (to make sure cities are properly handled)
	h = House("red", v[4], True)
	t.add_house(h, v[4])
	
	t.print_tile()
	
	# should be a free spot at v[2]
	print t.get_buildable_vertices()
	
	# add a house to the last free spot to make sure two-house rolls are properly handled
	t.add_house(House("purple", v[2]), v[2])
	
	print t.rolled()

#########################################
#	Written by Daniel Kats				#
#	August 1, 2012						#
#	Buildings used in Catan game		#
#########################################

class Building(object):
	'''Superclass for various building objects.'''
	
	def __init__(self, owner):
		'''Create a new building.'''
		
		self.__p = owner
		
	def player(self):
		'''Get the player who owns this structure.'''
		
		return self.__p

class House(Building):
	'''A settlement or a city.'''
	
	def __init__(self, owner, vertex=None, is_city = False):
		'''Create a new house.'''
		
		super(House, self).__init__(owner)
		
		self.__v = vertex
		self.__city = is_city
		
	def vertex(self):
		'''Get the coordinates of this house.'''
		
		return self.__v
		
	def points(self):
		'''Get the number of points this house is worth.'''
		
		return 2 if self.__city else 1
		
	def upgrade(self):
		'''Turn this settlement into a city.'''
		
		self.__city = True
		
	def is_city(self):
		'''Whether this is a settlement or a city.'''
		
		return self.__city
		
	def __str__(self):
		'''For debugging.'''
		
		m = "city" if self.is_city() else "settlement"
		
		return "{}'s {} at {}".format(self.player(), m, self.__v)

class Road(Building):
	'''One piece of road.'''
	
	def __init__(self, owner, v1=None, v2=None):
		'''Create a new road from v1 to v2.'''
		
		super(Road, self).__init__(owner)
		
		self.__v1 = v1
		self.__v2 = v2
		
		if not self._sanity_check():
			raise TypeError("{} and {} are too far apart".format(self.__v1, self.__v2))
		
	def _sanity_check(self):
		'''True if sanity check passes, False otherwise.
		Checks that vertices are exactly 1 unit apart.
		This may not be useful given the odd geometry.'''
		
		return abs(self.__v1[0] - self.__v2[0]) + abs(self.__v1[1] - self.__v2[1]) == 1
		
	def vertices(self):
		'''Return set of vertices, road goes from v[0] to v[1]'''
		
		return set([self.__v1, self.__v2])
		
	def __str__(self):
		'''For debugging.'''
		
		return "{}'s road from {} to {}".format(self.player(), self.__v1, self.__v2)

if __name__ == "__main__":
	r = Road((0, 0), (0, -1), "red")
	
	h = House((0, 0), "red")
	
	print(r)
	print(h)

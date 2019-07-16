class Resource(object):
	TYPES = ["brick", "ore", "wheat", "sheep", "wood", "desert"]

	def __init__(self, r):

		if r in Resource.TYPES:
			self.__r = r
		else:
			raise TypeError("Invalid type '{}'".format(r))

	def name(self):
		return self.__r

	def __str__(self):
		return self.name()

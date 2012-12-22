class Table():
	'''A table object, like an SQL table, but in memory.
	Terribly implemented and incomplete'''

	def __init__(self, headings):
		self._d = {}
		self._headings = headings
		
		for h in self._headings:
			self._d[h] = []
			self._sizing[h] = len(str(h))
		
	def insert(self, k, v):
		if k in self._d:
			self._d[k].append(v)
			
			if len(str(v)) > self._size[k]:
				self._size[k] = len(str(v))
		else:
			print "ERROR! {} not valid row".format(k)
	
	def draw_row(self, row):
		print " | ".join([str(val).center(self._sizing[self._headings[i]]) for i, val in enumerate(row)]) 
		
	def draw(self):
		self.draw_row(self._headings)
	
		for k, v in self._d.iteritems():
			draw_row(v)
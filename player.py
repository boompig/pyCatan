class Player():
	'''Single-player player.'''

	def __init__(self):
		'''Create a new Catan player.'''
		
		self._resources = {}
		self._vp = 0
		self._settlements = []
		self._roads = []
		
		# TODO here have stash of settlements, cities, roads that are unbuilt
		# TODO here have 
		
	def add_settlement(self, s):
		'''Add the given settlement to the list of settlements for this player.'''
		
		self._settlements.append(s)
		
	def add_road(self, v1, v2):
		'''Add a road.'''
		
		self._roads.append((v1, v2))
		
	def get_num_roads(self):
		'''Return number of roads built by this player.'''
		
		return len(self._roads)
	
	def get_num_settlements(self):
		'''Return the number of settlements this player has built.'''
		
		return len(self._settlements)
		
	def get_settlement(self, i):
		'''Return settlement at the given index.'''
		
		if i >= self._settlements:
			return None
		else:
			return self._settlements[i]
	

		
	def add_resources(self, resource_list):
		'''Collect resources.'''
		
		for r in resource_list:
			if r not in self._resources:
				self._resources[r] = 0
			self._resources[r] += 1
		
		#self._resources.extend(resource_list)
		
	def get_printable_hand(self):
		'''Return resources in the player's hand.'''
		
		s = ""
		
		for r, n in self._resources.iteritems():
			s += "{} x {}, ".format(r, n)
			
		return s[:-2]
		
	def get_resource_random_resource(self):
		'''Return (discard) random resource.'''
		
		pass
		
	def get_monopoly_resources(self, r):
		'''Get all resources of type r. Discard.'''
		
		pass
		
	def get_num_vp(self):
		'''Return number of victory points this player has.'''
	
		return self._vp
		
	def add_development_card(self, dc):
		'''Add given development card dc.'''
		
		pass
		
	def discard_resources(self, num):
		'''Discard num resources.
		Remove from player.
		Return the resources.
		Player chooses this
		'''
	
		pass
	
	def add_resource(self, r):
		'''Add resource r to this player's hand.'''
	
		pass
	
if __name__ == "__main__":
	p = Player()
	print p.get_num_vp()
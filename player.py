import random

class Player():
	'''Single-player player.'''

	def __init__(self):
		'''Create a new Catan player.'''
		
		self._resources = {}
		self._num_resources = 0
		
		self._vp = 0
		self._settlements = []
		self._roads = []
		
		# TODO here have stash of settlements, cities, roads that are unbuilt
		# TODO here have 
		
	def get_num_resources(self):
		'''Return the number of resources in the player's hand.'''
		
		return self._num_resources
		
	def can_deduct_resources(self, r_list):
		'''Return True iff can deduct all resources in r_list from this player.'''
		
		for r in set(r_list):
			num = r_list.count(r)
			if r not in self._resources or self._resources[r] < num:
				return False
		return True
		
	def deduct_resources(self, r_list):
		'''Deduct the given resources from the player. If not possible, return False.'''
		
		if not self.can_deduct_resources(r_list):
			return False
			
		for r in r_list:
			self._resources[r] -= 1
			self._num_resources -= 1
		return True
		
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
			self._num_resources += 1
		
		#self._resources.extend(resource_list)
		
	def get_printable_hand(self):
		'''Return resources in the player's hand.'''
		
		s = ""
		
		for r, n in self._resources.iteritems():
			s += "{} x {}, ".format(r, n)
			
		return s[:-2]
		
	def steal_resource(self):
		'''Return (discard) random resource. 
		If the player has no resources, return None.'''
		
		if self._num_resources == 0:
			return None
		
		n = random.randint(0, self.get_num_resources() - 1)
		i = 0
		
		for k in self._resources:
			if i <= n < i + self._resources[k]:
				self._resources[k] -= 1
				self._num_resources -= 1
				return k
			else:
				i += self._resources[k]
				
		print self._num_resources
		print n
		
	def get_monopoly_resources(self, r):
		'''Get all resources of type r. Discard.'''
		
		pass
		
	def get_num_vp(self):
		'''Return number of victory points this player has.'''
	
		return self._vp
		
	def add_development_card(self, dc):
		'''Add given development card dc.'''
		
		pass
	
	def get_hand(self):
		'''Return the player's hand.'''
		
		return self._resources
	
	def has_road_to(self, v):
		'''Return True iff this player has a road leading to vertex v.'''
		
		for road in self._roads:
			if v in road:
				return True
		return False
	
if __name__ == "__main__":
	p = Player()
	p.add_resources(["sheep"] * 3 + ["wheat"] * 2)
	#print p.steal_resource()
	#print p.steal_resource()
	#print p.steal_resource()
	#print p.steal_resource()
	
	print p.get_printable_hand()
	
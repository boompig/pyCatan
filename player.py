class Player():
	'''Single-player player.'''

	def __init__(self):
		pass
		
		self._resources = []
		self._vp = 0
		
		# TODO here have stash of settlements, cities, roads that are unbuilt
		# TODO here have 
		
	def collect_resources(self, dice_roll, map):
		'''Collect resources given the dice roll.'''
		
		pass
		
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
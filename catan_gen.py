'''
TODO I want to check in my code, and generate Catan maps
Then I can think about smart way to index these things
'''

'''
Honestly, my Python code is more ahead, probably.
0. 
	- appropriate way to index tile bodies, intersections, edges
	- to get this, need to see map...
	- edge = (v1, v2)
	- tile = ???

==> in order of operability

1.
a) Generate board (colors, numbers)

a2) Add clickable areas and differentiate between them
	- edges
	- vertices (nodes)
	- tiles (body)
	

b) Be able to add settlements, roads
	- small button at each intersection, that can disappear (deactivate - one time use) once a settlement is put there
	- oblong button (or clickable area) at the road
c) Be able to upgrade settlements to cities
	- again, button on settlement
	
d) Be able to add robber
	- button on tile
	
2. Single-player mechanics
	- dice rolling
	- turn-taking
		- being able to end the turn
	- production of resources, hand
	- robber event
		- move robber to new space
			- TODO do you have to move it or can you keep it in same place?
		- discard resources if too many cards
		- shut down production
	- building
		- using resources to place
		- not allowing for overlapping building
		- having limited number of resources
		- keeping track of VPs
	- victory points (solitary)
		- buildings
		- development cards
		- victory condition
		- showing number to be visible
	- development cards
		- using resources to get
		- having it be part of separate collection from resources
		- showing number to be visible
		- using them (solitary portions)
			- Knight - move robber
			- Year of Plenty
			- Road Building
			- VP cards
			
			- use limit: one per turn
	- achievement stats
		- longest contiguous road (this might be difficult yet fun)
		- number of revealed knights
			
3. Multi-player mechanics
	- turn-taking
		- rotate the turn
	- robber event
		- stealing resources
	- building
		- not allowing for overlapping buildings
	- victory points
		- victory condition
	- development cards
		- using them (multi-player)
			- Knight - stealing resources
			- Monopoly - stealing specific resource
	- trade
		- keep track of who is allowed to trade
	- achievement cards
		- longest road <-- keep track of # game-wide
			- the calculation here might be difficult
		- largest army <-- keep track of # game-wide
		
4. Graphics
	- dice
	- development cards
	- resource cards
	- buildings (cities, roads, settlements)
	- players themselves
		- VP count
		- resource count
		- development card count
		- number of played knights
		- longest contiguous road 
'''

def flatten_list(l):
	return [item for sublist in l for item in sublist]

class CatanConstants():
	'''Keep constants under one namespace.'''
	
	'''The number of tiles each resource has on a standard Catan board.'''
	resource_distribution = {
		"brick" : 3,
		"ore" : 3,
		"sheep" : 4,
		"wood" : 4,
		"wheat" : 4,
		"desert" : 1,
	}
	
	'''The layout of the tiles on a Catan board.
	Each entry represents number of tiles in successive row.'''
	tile_layout = (
		1,
		2, 
		3,
		2,
		3,
		2,
		3,
		2,
		1,
	)
	
	'''The way the tokens normally ride...'''
	token_map = {
		"a" : 5,
		"b" : 2,
		"c" : 6,
		"d" : 3,
		"e" : 8,
		"f" : 10,
		"g" : 9,
		"h" : 12,
		"i" : 11,
		"j" : 4,
		"k" : 8,
		"l" : 10,
		"m" : 9,
		"n" : 4,
		"o" : 5,
		"p" : 6,
		"q" : 3,
		"r" : 11,
	}
	
	'''We always make [2][0] = A and go CC.'''
	'''Same order every time - [2][0], [1][0], [0][0], [1][-1], [2][-1] ... '''
	
	@staticmethod
	def get_resource_distribution_pool():
		'''Return list of strings, where each string is a tile.'''
		
		l_start = [[k] * v for k, v in CatanConstants.resource_distribution.iteritems()]
		return flatten_list(l_start)

class CatanRenderConstants():
	resource_color_map = {
		"brick" : "firebrick",
		"wheat" : "goldenrod1",
		"sheep" : "yellow green",
		"ore" : "dark grey",
		"wood" : "forest green",
		"desert" : "DarkGoldenrod3",
	}
		
if __name__ == "__main__":
	print CatanConstants.get_resource_distribution_pool()
	
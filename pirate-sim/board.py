from token import Token
from tile import Tile
from resource import Resource
import random

class Board():
	'''A settlers of Catan board.
	Manage the board, mainly by creating it.
	Allow fast indexing for game actions.'''
	
	# map of resource names to number of tiles on board. DO NOT CHANGE.
	ResourceDistribution = \
	{
		"wood" : 4,
		"wheat" : 4,
		"sheep" : 4,
		"brick" : 3,
		"ore" : 3,
		"desert" : 1
	}
	
	# number of tiles in each row, from top to bottom. DO NOT CHANGE.
	Rows = [1, 2, 3, 2, 3, 2, 3, 2, 1]
	
	def __init__(self):
		'''Create a new Settlers board.'''
		
		self.r = {}
		self.__tiles = []
		
		# map of vertices to adjacent tiles
		self.__v_map = {}
		
		self.place_deck(self.make_tile_deck())
		
	def arrange_deck(self):
		'''Arrange the deck in the order it will be put down, as a list.
		Put the desert card somewhere randomly.'''
		
		letter_order = ["A", "K", "J" ,"L", "B", "Q", "M", "I", "R", "C", "P", "N", "H", "O", "D", "G", "E", "F"]
		
		pass
			
		
	def make_tile_deck(self):
		'''Create the unplaced tiles.'''
		
		deck = []
		
		for r, v in Board.ResourceDistribution.iteritems():
			for i in range(v):
				deck.append(Tile(Resource(r)))
				
		random.shuffle(deck)
				
		return deck
		
	def can_build(self, v):
		'''Check that vertex v is buildable.
		Does not check player roads, etc., only house proximity.'''
		
		pass
		
	def tokenize_deck(self, deck):
		'''Place the deck onto the board. Index in various ways.'''
		
		# all tokens
		all_tokens = Token.make_all_tokens()
		
		# sanity check - +1 for desert
		assert(len(all_tokens) + 1 == len(deck))
		
		for t in deck:
			# give it a NAME
			if t.name() != "desert": 
				t.place(all_tokens.pop(0))
			
			if t.number() not in self.r:
				self.r[t.number()] = []
			
			# map number to name of resource
			self.r[t.number()].append(t.name())
			
			# TODO consider mapping coordinates to resource
			# TODO map vertices to adjacent tiles
			# TODO add vertices here
			
			self.__tiles.append(t)
			
		return self.__tiles
		
	def get_rolled_tile(self, roll):
		return self.r[roll] if roll in self.r else []

#########################################
#	Written by Daniel Kats				#
#	August 1, 2012						#
#########################################

class Player(object):
	COLORS = ["red", "blue", "green", "yellow"]
	
	def __init__(self, color):
		# the color
		self.__c = color
	
		self.__cards = []
		
	def add_cards(self, cards):
		
		self.__cards.extend(cards)
		
	def color(self):
		return self.__c

	

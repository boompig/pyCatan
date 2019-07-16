#########################################
#	Written by Daniel Kats				#
#	August 1, 2012						#
#	This is a Settlers of Catan token	#
#########################################


def cmp(a, b):
	# see https://codegolf.stackexchange.com/a/49779/60645
	return (a > b) - (a < b)


class Token(object):
	'''Token placed on Catan tile. Has letter and number.'''

	def __init__(self, letter, number):

		# letter
		self.__l = letter
		# number
		self.__n = number

	def __str__(self):
		'''Print the token. For debugging.'''

		return "{} --> {}".format(self.__l, self.__n)

	def letter(self):
		'''Return token's letter.'''

		return self.__l

	def number(self):
		'''Return token's number.'''

		return self.__n

	def __cmp__(self, other):
		'''Compare to another token by letter.'''

		#print self
		#print other
		return cmp(self.letter(), other.letter())

	@staticmethod
	def make_tokens(letters, number):
		'''Make a token for every letter in letter list, associate it with given number.'''

		return [Token(letter, number) for letter in letters]

	@staticmethod
	def make_all_tokens():
		'''Make all tokens required for a game.
		Pulled this info from some site, hopefully correct.'''

		l = []

		l.extend(Token.make_tokens(["B"], 2))
		l.extend(Token.make_tokens(["D", "Q"], 3))
		l.extend(Token.make_tokens(["J", "N"], 4))
		l.extend(Token.make_tokens(["A", "O"], 5))
		l.extend(Token.make_tokens(["C", "P"], 6))
		l.extend(Token.make_tokens(["E", "K"], 8))
		l.extend(Token.make_tokens(["G", "M"], 9))
		l.extend(Token.make_tokens(["F", "L"], 10))
		l.extend(Token.make_tokens(["I", "R"], 11))
		l.extend(Token.make_tokens(["H"], 12))

		return l


import math

# ENUM FOR FLAG CONSTANTS
DB_TURN = 1
DB_BUILD = 2
DB_SUMMARY = 3

# DECLARE WHICH FLAGS ARE SET
flags = {
	DB_TURN : False,
	DB_BUILD : False,
	DB_SUMMARY : False
}

STRATEGY = 1

# Game constants
INCOME_TO_WIN = 3 + (4 * 3) + (4 * 2) + (2 * 3)
SETTLEMENT_COST = 7
STARTING_CAPITAL = 3


def DEBUG (flag, item):
	if flags[flag]:
		print(("DEBUG: {}".format(item)))


def get_turn (dice_roll_count):
	"""Return turn # based on # of dice rolls"""

	return math.floor ((dice_roll_count - 1) / 4) + 1


class CatanSimul (object):
	def __init__ (self, player, settlement_initial_quality):
		"""Run simul for the given player."""

		self.player = player
		self.dice_roll_count = 0
		self.total_income = STARTING_CAPITAL
		self.current_capital = STARTING_CAPITAL

		self.settlement_total_income = [0.0] * len (settlement_initial_quality)

		self.settlement_quality = []

		# self.settlement_quality = []
		for q in settlement_initial_quality:
			self.settlement_quality.append(q)

		self.granular_income = {
			'gold' : 0,
			'resources' : 0
		}

	def is_my_turn (self):
		return (self.dice_roll_count % 4) == (self.player % 4)

	def do_dice_roll (self):
		"""Do a dice roll. Adjust income accordingly. Part 1 of turn."""

		turn_income = 0.0
		# print ("a:" + self.settlement_quality)
		for i, q in enumerate(self.settlement_quality):
			self.settlement_total_income[i] += q
			self.total_income += q
			self.current_capital += q
			turn_income += q

		# here I'm not counting conversion to resources, just # of gold pieces
		assert turn_income < 1, "Pr. income should be < 1 every turn"
		self.granular_income['gold'] += (1 - turn_income)

	def build_settlement (self, settlement_quality):
		"""settlement_quality - Pr (resource) from this settlement"""

		DEBUG (DB_BUILD, "Built settlement at turn %d" % self.turn)

		# update simul data
		self.settlement_quality.append(settlement_quality)
		self.settlement_total_income.append(0)
		self.current_capital -= SETTLEMENT_COST

	def do_build (self):
		"""Build settlements based on given strategy"""

		# can only build on your turn
		if self.is_my_turn():

			# strategy 1: build shitty settlement at turn 3
			if STRATEGY == 1 and self.turn == 3:
				self.build_settlement (4 / 36)
			# strategy 2: build good settlement at turn 4
			elif STRATEGY == 2 and self.turn == 4:
				self.build_settlement(7 / 36)
			elif self.turn  > 4 and (self.current_capital >= 8) and (len (self.settlement_total_income) < 5):
				self.build_settlement(4 / 36)

	def do_simul (self):
		print(("Running experiment for player # %d" % self.player))

		while not (self.total_income >= INCOME_TO_WIN and self.is_my_turn()):
			self.dice_roll_count += 1
			self.turn = get_turn(self.dice_roll_count)

			self.do_dice_roll ()
			self.do_build ()

			DEBUG (DB_TURN, "Dice roll %d" % (self.dice_roll_count))
			DEBUG (DB_TURN, "Turn %d" % self.turn)
			DEBUG (DB_TURN, "Total income is %.2f" % self.total_income)

		win_turn = self.turn
		print(("Achieved win at turn %d" % win_turn))
		DEBUG (DB_SUMMARY, "Won with %d resources" % self.total_income)
		DEBUG (DB_SUMMARY, "")

		for i in range (len (self.settlement_total_income)):
			if i == 0:
				DEBUG (DB_SUMMARY, "Total income from initial harbour was %.2f" % (self.settlement_total_income[i]))
			elif i == 1:
				DEBUG (DB_SUMMARY, "Total income from initial settlement was %.2f" % (self.settlement_total_income[i]))
			else:
				DEBUG (DB_SUMMARY, "Total income from settlement %d was %.2f" % (i, self.settlement_total_income[i]))

		DEBUG (DB_SUMMARY, "")
		DEBUG (DB_SUMMARY, "Resource distribution:")
		for k, v in self.granular_income.items():
			DEBUG (DB_SUMMARY, "%s ==> %.2f" % (k, v))


if __name__ == "__main__":
	#print ("Income to win is %d" % income_to_win)
	print(("Running experiments for strategy %d" % STRATEGY))

	# turn debug flag on
	flags [DB_BUILD] = True

	## mallocing 2
	sq = [None] * 2

	# harbour; worst is 3 + 4, best is 4 + 5 (since no 5's are adjacent)
	l = [7 / 36, 8 / 36, 9 / 36]
	sq [0] = sum(l) / len(l)

	# first settlement; worst is 3 + 2 + 2; best is 4 + 4 + 5
	l = [7 / 36, 8 / 36, 9 / 36, 10 / 36, 11 / 36, 12 / 36, 13 / 36]
	sq [1] = sum(l) / len(l)

	for p in range (1, 5):
		#### SET INITIAL CONDITIONS
		# nothing to set

		##### RUN SIMULATION #####
		print ("")
		cs = CatanSimul(p, sq)
		cs.do_simul ()

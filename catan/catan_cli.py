'''
Play the game using AIs
'''

from ai.ai import AI
from ai.smart_placement_ai import SmartPlacementAI
from typing import Dict, List, Type
from argparse import ArgumentParser
import logging
from catan_tk import CatanApp
import random
from game_engine import Game, GameState
from ai.dummy_ai import DummyAI
import coloredlogs


class CatanCLI:
	def __init__(self, colors: List[str], ai_classes: Dict[str, Type[AI]], random_seed: int):
		random.seed(random_seed)
		lattice = CatanApp.get_hex_coord_lattice()
		self._colors = colors
		self._game = Game(
			starting_color=colors[0],
			colors=colors,
			hex_coord_lattice=lattice
		)
		self._ais = {}  # type: Dict[str, AI]
		for color in colors:
			self._ais[color] = ai_classes[color](color, self._game)

	def initial_placement(self):
		while self._game.get_state() == GameState.INITIAL_PLACEMENT:
			color = self._game.get_current_color()
			ai = self._ais[color]
			v = ai.get_settlement_placement(self._game)
			self._game.add_settlement(v, color, initial_placement=True)
			road = ai.get_road_placement(self._game, v)
			self._game.add_road(road[0], road[1], color, initial_placement=True)
			self._game.next_turn()

	def print_game_winner_status(self, winning_color: str) -> None:
		print(f"Winning player: {winning_color}")
		player = self._game.get_player(winning_color)
		ns = player.get_num_settlements()
		print(f"# settlements: {ns} ({ns} points)")
		nc = player.get_num_cities()
		print(f"# cities: {nc} ({nc * 2} points)")
		print(f"# development card VPs: {player.get_development_card_vp()} points")
		if player.has_special_card("longest road"):
			print("+ longest road (2 points)")
		if player.has_special_card("largest army"):
			print("+ largest army (2 points)")

		print(f"total points: {player.get_num_vp()}")

		print("")
		print(" ---- development cards ------")
		print(player.get_printable_dev_cards())

	def play_game(self) -> None:
		assert self._game.get_state() == GameState.ROLL_DICE
		turn = 1
		print("-" * 40)
		while not self._game.is_game_over and turn < 1000:
			color = self._game.get_current_color()
			print(f"Turn {turn} - {color}")
			player = self._game.get_player(color)
			print(f"{player.get_num_vp()} points")
			print(player.get_printable_hand())
			# player = self._game.get_player(color
			n = self._game.roll_dice()
			if n == 7:
				self._process_robber(color)
			ai = self._ais[color]
			ai.do_turn(self._game)
			self._game.next_turn()
			turn += 1
		self.print_game_winner_status(self._game.get_winning_player())

	def _process_robber(self, current_color: str):
		for color in self._colors:
			ai = self._ais[color]
			ai.robber_discard(self._game)
		ai = self._ais[current_color]
		steal_from_player, coords = ai.get_robber_placement(self._game)
		self._game.move_robber(coords, steal_from_player, current_color)


def setup_logging(verbose: bool):
	log_level = (logging.DEBUG if verbose else logging.INFO)
	logging.basicConfig(level=log_level)
	coloredlogs.install(level=log_level)


if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument("-v", "--verbose", action="store_true")
	parser.add_argument("--seed", default=42,
		help="random seed to use for random number generator")
	args = parser.parse_args()
	setup_logging(args.verbose)
	ais = {}  # type: Dict[str, Type[AI]]
	colors = ["red", "orange", "blue", "green"]
	ais["red"] = SmartPlacementAI
	for color in colors[1:]:
		ais[color] = DummyAI
	g = CatanCLI(colors, ais, args.seed)
	g.initial_placement()
	g.play_game()

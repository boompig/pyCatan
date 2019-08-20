import random
from settlement import Settlement
from typing import List, Dict, Optional, Set
from catan_types import Vertex, Edge
from catan_gen import CatanConstants
import logging


logger = logging.getLogger(__name__)


class DevelopmentCardError(Exception):
	pass


class Player:
	'''Single-player player.'''

	def __init__(self, color) -> None:
		'''Create a new Catan player.'''

		self._resources = {}  # type: Dict[str, int]
		self._color = color

		# this variable stores the *permanent* victory points
		# this does not include temporary victory points such as special cards
		self._vp = 0
		self._dev_card_vp = 0

		self._settlements = {}  # type: Dict[Vertex, Settlement]
		self._settlement_order = []  # type: List[Settlement]
		self._roads = []  # type: List[Edge]

		self._dev_cards = {}  #type: Dict[str, int]
		self._special_cards = set([])  # type: Set[str]
		self._num_knights_played = 0

	def get_color(self) -> str:
		return self._color

	def get_num_resources(self) -> int:
		'''Return the number of resources in the player's hand.'''

		return sum([v for v in self._resources.values()])

	def can_deduct_resources(self, r_list: List[str]) -> bool:
		'''Return True iff can deduct all resources in r_list from this player.'''

		for r in set(r_list):
			num = r_list.count(r)
			if r not in self._resources or self._resources[r] < num:
				# logger.warning("Cannot deduct resources %s from player %s", r_list, self._color)
				return False
		return True

	def deduct_resources(self, r_list: List[str]) -> None:
		'''Deduct the given resources from the player. If not possible, throw Exception.'''

		if not self.can_deduct_resources(r_list):
			raise Exception("Cannot deduct these resources")

		for r in r_list:
			self._resources[r] -= 1
			# if this part is disabled, will have zeroes as values for some resources
			# if enabled, then some resources will not be in the dict
			#if self._resources[r] == 0:
			#	del(self._resources[r])

	def add_settlement(self, v: Vertex, s: Settlement) -> None:
		'''Add the given settlement to the list of settlements for this player.'''

		self._settlements[v] = s
		self._settlement_order.append(s)
		self._vp += 1

	def get_settlement(self, i: int) -> Settlement:
		return self._settlement_order[i]

	def upgrade_settlement_to_city(self, vertex: Vertex) -> None:
		'''Update a city of this player.
		Used to update VP count.'''

		assert self.has_settlement_at(vertex)
		self._vp += 1

	def add_road(self, v1: Vertex, v2: Vertex) -> None:
		'''Add a road.'''

		self._roads.append((v1, v2))

	def get_num_roads(self) -> int:
		'''Return number of roads built by this player.'''

		return len(self._roads)

	def get_num_settlements(self) -> int:
		'''Return the number of settlements this player has built.'''

		return len([s for s in self._settlement_order if not s.is_city()])

	def get_num_cities(self):
		return len([s for s in self._settlement_order if s.is_city()])

	def get_settlements(self) -> List[Settlement]:
		return self._settlement_order

	def get_settlement_vertices(self) -> List[Vertex]:
		"""Vertices are returned in no particular order"""
		return [v for v in self._settlements.keys()]

	def add_resources(self, resource_list: List[str]) -> None:
		'''Collect resources.'''

		for r in resource_list:
			assert r != "desert"
			if r not in self._resources:
				self._resources[r] = 0
			self._resources[r] += 1

		#self._resources.extend(resource_list)

	def get_printable_hand(self) -> str:
		'''Return resources in the player's hand.'''

		s = ""

		for r, n in self._resources.items():
			s += "{} x {}, ".format(r, n)

		return s[:-2]

	def get_printable_dev_cards(self) -> str:
		'''Return development cards in the player's hand.'''

		s = ""

		for r, n in self._dev_cards.items():
			if n == 0:
				continue
			s += "{} x {}, ".format(r, n)

		return s[:-2]

	def steal_resource(self) -> Optional[str]:
		'''Return (discard) random resource.
		If the player has no resources, return None.'''

		num_resources = self.get_num_resources()

		if num_resources == 0:
			return None

		n = random.randint(0, num_resources - 1)
		i = 0

		for k in self._resources:
			if i <= n and n < i + self._resources[k]:
				self._resources[k] -= 1
				return k
			else:
				i += self._resources[k]
		raise Exception("Fail")

	def get_num_vp(self) -> int:
		'''Return number of victory points this player has.'''

		vp = self._vp
		for card in self._special_cards:
			vp += CatanConstants.special_card_points[card]
		return vp

	def add_special_card(self, card: str) -> None:
		self._special_cards.add(card)

	def remove_special_card(self, card: str) -> None:
		self._special_cards.remove(card)

	def has_special_card(self, card: str) -> bool:
		return card in self._special_cards

	def add_development_card(self, card: str) -> None:
		'''Add given development card.'''

		self._dev_cards.setdefault(card, 0)
		self._dev_cards[card] += 1
		if card == "VP":
			self._vp += 1
			self._dev_card_vp += 1

	def get_development_card_vp(self) -> int:
		return self._dev_card_vp

	def get_num_knights_played(self) -> int:
		return self._num_knights_played

	def play_development_card(self, card: str) -> None:
		'''Remove the given development card from development cards
		This development card is not a VP card.
		NOTE: this does not actually play the card, only sets the card as played here'''

		if card not in self._dev_cards or self._dev_cards[card] == 0:
			raise DevelopmentCardError(f"This player does not have development card {card}")

		self._dev_cards[card] -= 1
		if card == "knight":
			self._num_knights_played += 1

	def get_development_cards(self) -> Dict[str, int]:
		'''Return development cards for this player.'''

		return self._dev_cards

	def get_hand(self) -> Dict[str, int]:
		'''Return the resources in the player's hand (copy).'''
		return self._resources.copy()

	def has_road_to(self, v: Vertex) -> bool:
		'''Return True iff this player has a road leading to vertex v.'''

		for road in self._roads:
			if v in road:
				return True
		return False

	def has_settlement_at(self, v: Vertex) -> bool:
		return v in self._settlements

	def get_road_vertices(self) -> Set[Vertex]:
		vs = set([])
		for road in self._roads:
			vs.add(road[0])
			vs.add(road[1])
		return vs

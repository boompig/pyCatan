#############################
#	Written by Daniel Kats	#
#	December 25, 2012		#
#############################

from catan_gen import CatanConstants
from utils import CatanUtils
from typing import Optional, Tuple
from catan_types import HexCoord, Vertices


class Hex():
	'''
	This is a hex-tile on the catan board.
	Add methods as needed.
	'''

	def __init__(self, resource: str) -> None:
		self._resource = resource
		self._tile_type = ""
		self._number = -1
		# coordinates of vertices
		self._vertices = None  # type: Optional[Vertices]
		self._coord = None  # type: Optional[HexCoord]

	def get_resource(self) -> str:
		return self._resource

	def set_coord(self, coord: HexCoord) -> None:
		self._coord = coord

	def get_coord(self) -> HexCoord:
		assert self._coord is not None
		return self._coord

	def set_vertices(self, vertices: Vertices) -> None:
		self._vertices = vertices

	def get_vertices(self) -> Vertices:
		assert self._vertices is not None
		return self._vertices

	def set_token(self, t: str) -> None:
		self._tile_type = t
		self._number = CatanConstants.token_map[self._tile_type]

	def get_number(self) -> Optional[int]:
		return self._number

	def get_token(self):
		'''Return the token letter associated with this hex.
		If it is a desert hex, return the string "DESERT"'''

		if self._tile_type is None:
			return "DESERT"
		else:
			return self._tile_type

	def get_num_dots(self) -> int:
		'''Return the number of dots on the token for this hex.'''

		if self._number is None:
			return 0
		else:
			return CatanUtils.get_num_token_dots(self._number)

	def get_vertex(self, index):
		if isinstance(index, int):
			return self._vertices[index]
		elif isinstance(index, str):
			if index == "left":
				return self._vertices[0]
			elif index == "right":
				return self._vertices[3]

	def get_center(self) -> Tuple[float, float]:
		'''Return the center of this tile.'''

		return (
			(self.get_left() + self.get_right()) / 2,
			(self.get_top() + self.get_bottom()) / 2,
		)

	def get_top(self) -> int:
		assert self._vertices is not None
		return self._vertices[1][1]

	def get_bottom(self) -> int:
		assert self._vertices is not None
		return self._vertices[-1][1]

	def get_left(self) -> int:
		assert self._vertices is not None
		return self._vertices[0][0]

	def get_right(self) -> int:
		assert self._vertices is not None
		return self._vertices[3][0]

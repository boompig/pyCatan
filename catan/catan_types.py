from typing import Tuple, List


Vertex = Tuple[int, int]
Edge = Tuple[Vertex, Vertex]
HexCoord = Tuple[int, int]
Vertices = Tuple[Vertex, Vertex, Vertex, Vertex, Vertex, Vertex]
LatticeRow = List[Vertices]
Lattice = List[LatticeRow]
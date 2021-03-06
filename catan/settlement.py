from typing import Tuple


class Settlement():
    '''Representation for a city or settlement.'''

    def __init__(self, vertex: Tuple[int, int], color: str) -> None:
        '''Create a new settlement of given color at given vertex.'''

        self._vertex = vertex
        self._color = color
        self._city = False

    def is_city(self) -> bool:
        '''Return True iff this settlement is actually a city.'''

        return self._city

    def upgrade(self) -> None:
        '''Upgrade this settlement to a city.'''

        self._city = True

    def vertex(self) -> Tuple[int, int]:
        '''Return the vertex at which this city/settlement is placed.'''

        return self._vertex

    def color(self) -> str:
        '''Return the color of this city/settlement.'''

        return self._color

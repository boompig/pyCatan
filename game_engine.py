'''
This file maintains the state of the overall gameplay
'''

import random
from collections import deque
from catan_gen import CatanConstants
from hex import Hex
from player import Player
from settlement import Settlement
from ai import AI
from typing import Dict, List, Set, Optional
from catan_types import Vertex, Edge
import logging


logger = logging.getLogger(__name__)


class SettlementPlacementException(Exception):
    pass


class DevelopmentCardError(Exception):
    pass


class MapGen():
    '''Engine for generating Catan maps.'''

    def __init__(self) -> None:
        self._decr_set = set([1, 2, 4, 6])
        self._players = {}  # type: Dict[str, Player]
        self.ai = AI(self)
        self._dev_card_deck = []  # type: List[str]
        # list of rows, where each row is a list of Hex tiles
        self._board = []  # type: List[List[Hex]]
        self._settlements = {}  # type: Dict[Vertex, Settlement]
        self._roads = set([])  # type: Set[Edge]

        self._vertex_map = {}  # type: Dict[Vertex, List[Hex]]
        self._vertex_set = set([])  # type: Set[Vertex]
        self._road_set = set([])  # type: Set[Edge]
        self._resource_map = {}  # type: Dict[int, List[Hex]]

        # where do the special cards reside?
        self._longest_road_player = None  # type: Optional[Player]
        self._largest_army_player = None  # type: Optional[Player]
        self._longest_road_length = 0
        self._largest_army_num_knights = 0

    def _make_dev_card_deck(self) -> None:
        '''Create a shuffled deck of development cards.'''

        self._dev_card_deck = []

        for card, num in CatanConstants.development_cards.items():
            self._dev_card_deck.extend([card] * num)

        random.shuffle(self._dev_card_deck)

    def gen(self) -> None:
        # this is a mapping of rows to hexes...
        self._board = []

        # create hexes with resources, shuffle
        deck = self._make_deck()

        # arrange deck on the board (so create placement)
        self._place_tiles(deck)

        # assign tokens
        self._assign_tokens()

        # and draw it
        self.draw()

        # create development card deck
        self._make_dev_card_deck()

    def play_development_card(self, color, card):
        '''Player with given color plays given card. Process effects.'''

        raise NotImplementedError()

    def get_player_vp(self, color: str) -> int:
        '''Return number of victory points for player of given color.'''

        p = self.get_player(color)
        return p.get_num_vp()

    def get_development_card(self, color: str) -> str:
        '''Give out a development card to the player if they can afford it.
        Return the development card, or None if none given.'''

        p = self.get_player(color)
        cost = CatanConstants.development_card_cost

        if p.can_deduct_resources(cost) and len(self._dev_card_deck) > 0:
            p.deduct_resources(cost)
            card = self._dev_card_deck.pop()
            p.add_development_card(card)
            return card
        elif len(self._dev_card_deck) == 0:
            raise DevelopmentCardError(f"There are no more development cards left");
        else:
            raise DevelopmentCardError(f"Player {color} cannot afford to buy a development card");

    def create_players(self, colors: List[str]) -> None:
        '''Create brand new players. For now, they are just placeholders.'''

        for c in colors:
            self._players[c] = Player()

    def get_player(self, color: str) -> Player:
        '''Return the player with the given color.'''

        return self._players[color]

    def _assign_tokens(self) -> None:
        '''Assign tokens to the tiles on the board.'''

        # a reversed list of letters (so pop operation works)
        letters = deque(reversed(sorted(CatanConstants.token_map.keys())))
        unplaced_layout = { row : col for row, col in enumerate(CatanConstants.tile_layout) }

        # start in corner (0, 2)
        row = 2
        col = 0
        #print min(unplaced_layout.keys())

        # do this for all the letters
        while len(letters) > 0:

            # withdraw a letter from the map
            if self._board[row][col].get_resource() != "desert":
                l = letters.pop()
                #print "{} ==> {}".format((row, col), l)
                self._board[row][col].set_token(l)
            #else:
            #print "desert at {}".format((row, col))

            unplaced_layout[row] -= 1

            if unplaced_layout[row] == 0:
                del(unplaced_layout[row])

            if len(unplaced_layout) > 0:
                row, col = self._get_next_tile(row, col, unplaced_layout)


    def _get_next_tile(self, row: int, col: int, unplaced_layout: Dict[int, int]) -> Vertex:
        '''Calculate next tile position from this tile position when placing tokens.'''

        if row == 4 and col == 0:
            return (3, 0) # starting tile for loop 1
        elif row not in [3, 5] and col in [0, -1]:
            loop_i = 0
        elif row == 5 and col == 0:
            return (4, 1) # only element in loop 2
        else:
            loop_i = 1

        if loop_i == 0:
            # change column
            if row == 8:
                col = 0
            elif row == 0:
                col = -1

            row_incr = -1 if ((col == 0 and row > 0) or row == 8)  else 1
            row += row_incr


            if row in [3, 5]: # skip over these rows
                row += row_incr
        elif loop_i == 1:
            # note the (5, 0) case taken care of above

            if row == 2:
                row, col = (3, -1)
            elif row == 3 and col == 0:
                row, col = (2, 1)
            elif row == 3 and col == -1:
                row, col = (5, -1)
            elif row == 5 and col == -1:
                row, col = (6, 1)
            elif row == 6:
                row, col = (5, 0)

        return (row, col)

    def _place_tiles(self, deck: List[str]) -> None:
        '''Place tiles on the board.'''

        for row_num, num_cols in enumerate(CatanConstants.tile_layout):
            row = []  # type: List[Hex]
            self._board.append(row)

            for col in range(num_cols):
                row.append(Hex(deck.pop()))

    def _make_deck(self) -> List[str]:
        '''Return a shuffled deck of unplaced resources.'''

        deck = CatanConstants.get_resource_distribution_pool()
        random.shuffle(deck)
        return deck

    def draw_ascii(self):
        '''Render the board in a terminal.'''

        f = lambda hex: hex.get_token()

        for row in self._board:
            if len(row) == 3:
                print(" ".join([f(c) for c in row]))
            elif len(row) == 2:
                print(" " + " ".join([f(c) for c in row]) + " ")
            elif len(row) == 1:
                print((2 * " ") + f(row[0]) + (2 * " "))

    def prepare(self) -> None:
        '''Create optimized data structures for easy access to some common game data.'''

        # TODO
        #CatanApp.set_vertices(self._board) # this part is important
        self._create_resource_map()
        self._create_vertex_map()
        self._create_vertex_set()
        self._create_road_set()

        self._settlements = {}
        self._roads = set([])

        # this is the available set of nodes on which settlements can be built
        self.available_settlement_set = self._vertex_set.copy()

        # place the robber on the desert hex
        self._find_desert_hex()
        self._robber_hex = self._desert_pos
        #self._robber_hex = self._resource_map["desert"][0]

        self.ai.prepare()

    def _find_desert_hex(self) -> None:
        '''Find the desert hex and set self._desert_pos to its position in the form (row, col).'''

        for row_i, row in enumerate(self._board):
            for col, hex in enumerate(row):
                if hex.get_resource() == "desert":
                    self._desert_pos = (row_i, col)
                    return

    def cull_bad_settlement_vertices(self, v: Vertex) -> None:
        '''Given that a settlement was built on vertex v, remove adjacent vertices from the
        set of viable building nodes for settlements. Also remove that vertex.'''

        adjacent_v_set = set(self.get_adjacent_vertices(v))
        self.available_settlement_set.difference_update(adjacent_v_set)
        self.available_settlement_set.discard(v)

    def get_nodes(self) -> Set[Vertex]:
        return self._vertex_set

    def _has_road(self, v1: Vertex, v2: Vertex) -> bool:
        '''True iff the road from v1 to v2 has been built.'''

        return (v1, v2) in self._roads

    def _road_connects_same_color_settlement(self, v1: Vertex, v2: Vertex, color: str) -> bool:
        '''True iff this road connects to a settlement of the same color.'''

        return (v1 in self._settlements and self._settlements[v1].color() == color) or \
            (v2 in self._settlements and self._settlements[v2].color() == color)

    def _road_connects_same_color_road(self, v1: Vertex, v2: Vertex, color: str) -> bool:
        '''True iff this road connects to another road of the same color.'''

        return self.get_player(color).has_road_to(v1) or self.get_player(color).has_road_to(v2)

    def _normalize_road(self, v1: Vertex, v2: Vertex):
        if v1[0] > v2[0]:
            return (v2, v1)
        else:
            return (v1, v2)

    def add_road(self, v1: Vertex, v2: Vertex, color: str, ignore_cost: bool = False) -> bool:
        '''Add a road of the given color to the map. Charge the player for it.
        Rules:
        - (v1, v2) is not an existing road
        - at least one of (v1, v2) must connect to a same color settlement OR
        - at least one of (v1, v2) must connect to a same color road
        Road spans between v1 and v2.'''

        v1, v2 = self._normalize_road(v1, v2)

        p = self.get_player(color)
        cost = CatanConstants.building_costs["road"]

        # first condition only applies to first 2 roads
        if (self._has_road(v1, v2) or
            not (self._road_connects_same_color_settlement(v1, v2, color) or
                 (self._road_connects_same_color_road(v1, v2, color) and
                  p.get_num_roads() >= 2))):
            return False
        elif p.get_num_roads() >= 2 and not p.can_deduct_resources(cost):
            return False
        else:
            self._roads.add((v1, v2))
            if p.get_num_roads() >= 2:
                p.deduct_resources(cost)
            p.add_road(v1, v2)
            # now figure out whether this makes this road the longest road

            road_length = self._get_road_length(v1, color)
            logger.debug(f"{color}'s new road has length {road_length}")
            if ((self._longest_road_player is None and road_length >= 5) or
                    (road_length > self._longest_road_length)):
                if self._longest_road_player:
                    self._longest_road_player.remove_special_card("longest road")
                    if self._longest_road_player != p:
                        logger.info(f"{self._longest_road_player} lost longest road card")
                p.add_special_card("longest road")
                logger.info(f"{color} now has longest road with a road length of {road_length}")
                self._longest_road_length = road_length
                self._longest_road_player = p
                logger.info(f"{p} now has longest road card")
            return True

    def _get_road_length(self, starting_vertex: Vertex, color: str, visited: Optional[Set[Vertex]] = None) -> int:
        '''Get the longest portion of this road starting from the given vertex'''
        if visited is None:
            visited = set([])
        lengths = []
        # first, find all the adjacent vertices
        player = self.get_player(color)
        visited2 = visited.copy()
        visited2.add(starting_vertex)
        for v2 in self.get_adjacent_vertices(starting_vertex):
            if v2 in visited:
                continue
            if player.has_road_to(v2):
                lengths.append(1 + self._get_road_length(v2, color, visited2))

        # highest lengths first
        lengths.sort(reverse=True)
        if lengths == []:
            return 0
        elif len(lengths) == 1:
            return lengths[0]
        else:
            return lengths[0] + lengths[1]

    def has_road(self, v1: Vertex, v2: Vertex) -> bool:
        '''Return true iff a road from v1 to v2 has already been built.
        Also allows for a road from v2 to v1'''

        if v1[0] > v2[0]:
            v1, v2 = v2, v1 # switch places

        return (v1, v2) in self._roads

    def add_settlement(self, v: Vertex, color: str) -> bool:
        '''Add a settlement of the given color to the map.
        Deduct the cost if building is in a valid place.
        Return False if cannot afford or cannot build.'''

        if v not in self.available_settlement_set:
           return False

        p = self.get_player(color)
        cost = CatanConstants.building_costs["settlement"]

        # cannot build settlements in the middle of nowhere
        if p.get_num_settlements() >= 2 and not p.has_road_to(v):
            return False

        if p.get_num_settlements() >= 2 and not p.can_deduct_resources(cost):
            return False

        if v in self._vertex_set:
            if p.get_num_settlements() >= 2:
                p.deduct_resources(cost)

            s = Settlement(v, color)
            self._settlements[v] = s # add to the game board
            p.add_settlement(s) # add to player for record-keeping
            self.cull_bad_settlement_vertices(v) # make sure nothing can be built around it

            return True
        else:
            return False

    def get_players_on_robber_hex(self):
        '''Return a list of player colors on the hex with the robber.'''

        s = set([])

        for v in self.get_robber_hex().get_vertices():
            if v in self._settlements:
                s.add(self._settlements[v].color())

        return list(s)


    def add_city(self, v: Vertex, color: str) -> bool:
        '''Add a city of the given color to the map.
        Upgrades existing settlement.
        Deduct the cost if building is in a valid place.
        Return False if cannot afford or cannot build.'''

        cost = CatanConstants.building_costs["city"]
        p = self.get_player(color)

        if v not in self._settlements \
        or self._settlements[v].is_city() \
        or self._settlements[v].color() != color:
            return False
        elif not p.can_deduct_resources(cost):
            return False
        else:
            self._settlements[v].upgrade()
            p.deduct_resources(cost)
            p.update_city()
            return True

    def _create_vertex_set(self) -> None:
        '''Create a set of all vertices (nodes) on the map.
        Used in settlement placement.'''

        self._vertex_set = set(self._vertex_map.keys())

    def _create_vertex_map(self) -> None:
        ''' vertex_map maps coordinates to list of hexes
        Used to quickly determine adjacency when settlement is placed. '''

        self._vertex_map = {}

        for row in self._board:
            for hex in row:
                for v in hex.get_vertices():
                    if v not in self._vertex_map:
                        self._vertex_map[v] = []
                    self._vertex_map[v].append(hex)

    def produce(self, s: Settlement, ignore_robber: bool = False) -> List[str]:
        '''Make the settlement s produce resources.
        Hex with the robber does not produce unless explicitly told (ignore_robber=True).
        Return a list of the resources produced.'''

        l = []
        v = s.vertex()
        adjacent_hex_list = self._vertex_map[v]
        for hex in adjacent_hex_list:
            if hex != self.get_robber_hex() or ignore_robber:
                l.append(hex.get_resource())

        self._players[s.color()].add_resources(l)
        return l

    def get_resources_produced(self, roll: int) -> Dict[str, List[str]]:
        '''For the given roll, return a map of player color to resources produced.'''

        d = {}  # type: Dict[str, List[str]]

        if roll == 7:
            return d # no resources ever produced on a seven

        for hex in self._resource_map[roll]:
            r = hex.get_resource()

            for v in hex.get_vertices():
                if v in self._settlements:
                    s = self._settlements[v]
                    c = s.color()

                    if c not in d:
                        d[c] = []

                    if s.is_city():
                        d[c].extend([r, r])
                    else:
                        d[c].append(r)

        # now add these resources to the relevant players
        for p, r_list in d.items():
            self._players[p].add_resources(r_list)

        return d

    def get_adjacent_vertices(self, v: Vertex) -> Set[Vertex]:
        '''Return all vertices adjacent to vertex v.'''

        adjacent_v = set([])

        # first, get tiles that v1 is a member of
        adjacent_hexes = self._vertex_map[v]

        # adjacent vertices are found only in adjacent tiles
        for hex in adjacent_hexes:
            v_set = hex.get_vertices()
            v_i = v_set.index(v) # we know that this exists
            # on each tile, adjacent vertices are +1 and -1 index away
            adjacent_v.update([v_set[v_i - 1], v_set[(v_i + 1) % len(v_set)]])

        return adjacent_v

    def _create_road_set(self) -> None:
        '''Compile a set of tuples, each of which is a valid road.'''

        self._road_set = set([])

        for v in self._vertex_set:
            v_road_set = set([(v, v2) for v2 in self.get_adjacent_vertices(v)])
            self._road_set.update(v_road_set)

    def get_roads(self) -> Set[Edge]:
        return self._road_set

    def robber_discard(self):
        '''Return map of color to number of resources each player must discard.'''

        d = {}

        for c, p in self._players.items():
            if p.get_num_resources() > 7:
                d[c] = p.get_num_resources() // 2 # explicit integer division

        return d

    def _get_hex_at_coords(self, row: int, col: int) -> Hex:
        '''Return hex object at the given coordinates.'''

        return self._board[row][col]

    def get_robber_hex(self) -> Hex:
        '''Return the hex with the robber on it.'''

        #return self._robber_hex
        return self._get_hex_at_coords(*self._robber_hex)

    def set_robber_hex(self, row: int, col: int) -> bool:
        '''Set the position of the robber.
        Cannot be same as old position.
        Return True iff robber was properly set.'''

        if (row, col) == self._robber_hex:
            #print "Robber cannot go on same space!!"
            return False
        else:
            self._robber_hex = (row, col)
            return True
            #self._board[row][col]

    def robber_steal(self, from_player: str, to_player: str) -> Optional[str]:
        '''Robber steals from from_player and gives to to_player.
        Return the resource that was stolen.
        If from_player has no cards, return None.'''

        r = self._players[from_player].steal_resource()

        if r is not None:
           self._players[to_player].add_resources([r])

        return r

    def _create_resource_map(self) -> None:
        ''' resource_map maps numbers to list of hexes
        Used in resource distribution when dice are rolled.'''

        self._resource_map = {}
        for row in self._board:
            for hex in row:
                num = hex.get_number()
                if num is None:
                    # this is the desert hex and is excluded from the resource map
                    continue
                self._resource_map.setdefault(num, [])
                self._resource_map[num].append(hex)


    def get_map(self) -> List[List[Hex]]:
        return self._board

    def draw(self) -> None:
        '''Render the board.'''

        pass

def gen_map():
    '''Generate a map in the map generator.
    Print ASCII representation of the map'''

    mg = MapGen()
    mg.gen()
    mg.prepare()

    print(mg._road_set)

    mg.draw_ascii()

if __name__ == "__main__":
    gen_map()

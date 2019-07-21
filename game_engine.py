'''
This file maintains the state of the overall gameplay
'''

import random
from collections import deque
from catan_gen import CatanConstants
from hex import Hex
from player import Player
from settlement import Settlement
from typing import Dict, List, Set, Optional
from catan_types import Vertex, Edge
import logging
from enum import Enum, auto


logger = logging.getLogger(__name__)


class SettlementPlacementError(Exception):
    pass


class DevelopmentCardError(Exception):
    pass


class CityUpgradeError(Exception):
    pass


class RoadPlacementError(Exception):
    pass


class GameState(Enum):
    # FIRST_SETTLEMENT_PLACEMENT = auto()
    # SECOND_SETTLEMENT_PLACEMENT = auto()
    # FIRST_ROAD_PLACEMENT = auto()
    # SECOND_ROAD_PLACEMENT = auto()
    INITIAL_PLACEMENT = auto()
    ROLL_DICE = auto()
    GAMEPLAY = auto()


class Game():
    '''Engine for generating Catan maps.'''

    def __init__(self, starting_color: str,
                 colors: List[str],
                 hex_coord_lattice) -> None:
        self._decr_set = set([1, 2, 4, 6])
        self._players = {}  # type: Dict[str, Player]
        self._dev_card_deck = []  # type: List[str]
        # list of rows, where each row is a list of Hex tiles
        self._board = []  # type: List[List[Hex]]
        self._settlements = {}  # type: Dict[Vertex, Settlement]
        self._roads = set([])  # type: Set[Edge]

        self._vertex_map = {}  # type: Dict[Vertex, List[Hex]]
        self._vertex_set = set([])  # type: Set[Vertex]
        self._road_set = set([])  # type: Set[Edge]
        self._resource_map = {}  # type: Dict[int, List[Hex]]

        self._is_game_over = False
        # index into self.colors
        self._turn = colors.index(starting_color)
        self._colors = colors
        self._state = GameState.INITIAL_PLACEMENT
        self._hex_coord_lattice = hex_coord_lattice
        # placement goes to the last player, then comes back
        # this variable keeps track of which way we're going
        self._placement_count = 0

        # where do the special cards reside?
        self._longest_road_player = None  # type: Optional[Player]
        self._largest_army_player = None  # type: Optional[Player]
        self._longest_road_length = 0
        self._largest_army_num_knights = 0

        self._create_players(self._colors)
        self._generate_board()
        self._make_dev_card_deck()
        self._prepare_data_structures()

    def _make_dev_card_deck(self) -> None:
        '''Create a shuffled deck of development cards.'''

        self._dev_card_deck = []
        for card, num in CatanConstants.development_cards.items():
            self._dev_card_deck.extend([card] * num)
        random.shuffle(self._dev_card_deck)

    def _generate_board(self) -> None:
        '''Generate the board randomly'''
        # create hexes with resources, shuffle
        tile_deck = self._get_random_tile_deck()
        # arrange deck on the board (so create placement)
        self._place_tiles(tile_deck)
        # assign tokens
        self._assign_tokens()
        # once the board is set, have to set vertices for the hexes
        for row_i, row in enumerate(self._board):
            for col_i, hex in enumerate(row):
                hex.set_vertices(self._hex_coord_lattice[row_i][col_i])

    @property
    def is_game_over(self) -> bool:
        return self._is_game_over

    def roll_dice(self) -> int:
        '''
        Roll the dice and distribute resources based on the outcome
        It is up to the caller to handle a 7 (robber and discard events)'''
        assert self._state == GameState.ROLL_DICE, f"Current state is {str(self._state)}"
        r1 = random.randint(1, 6)
        r2 = random.randint(1, 6)
        roll = r1 + r2
        self.produce_resources_from_roll(roll)
        self._state = GameState.GAMEPLAY
        return roll

    def check_game_over(self):
        '''Check whether the game is over and set appropriate variables'''
        for _, player in self._players.items():
            if player.get_num_vp() >= 10:
                self._is_game_over = True
                break

    def next_turn(self) -> None:
        '''Roll over to the next turn'''
        assert self._state != GameState.ROLL_DICE, "Cannot end turn before rollling dice"
        if self._state == GameState.GAMEPLAY:
            self.check_game_over()
            self._turn = (self._turn + 1) % len(self._colors)
            self._state = GameState.ROLL_DICE
        elif self._state == GameState.INITIAL_PLACEMENT:
            placement_dir_forward = self._placement_count < len(self._colors)
            if self._placement_count + 1 == len(self._colors):
                # don't change the turn
                # going the other way now
                pass
            elif self._placement_count + 1 == 2 * len(self._colors):
                # don't change the turn
                # we're done placement
                pass
            elif placement_dir_forward:
                self._turn = (self._turn + 1) % len(self._colors)
            else:
                self._turn = (self._turn - 1 + len(self._colors)) % len(self._colors)
            self._placement_count += 1
            logger.debug("placement count=%d, next turn = %s" % (self._placement_count, self._colors[self._turn]))

            if self._placement_count == 2 * len(self._colors):
                self.__end_initial_placement()

    def get_current_color(self) -> str:
        return self._colors[self._turn]

    def play_development_card(self, color, card):
        '''Player with given color plays given card. Process effects.'''

        raise NotImplementedError()

    def get_player_vp(self, color: str) -> int:
        '''Return number of victory points for player of given color.'''

        p = self.get_player(color)
        return p.get_num_vp()

    def has_development_cards(self) -> bool:
        return len(self._dev_card_deck) > 0

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

    def _create_players(self, colors: List[str]) -> None:
        '''Create brand new players. For now, they are just placeholders.'''

        for color in colors:
            self._players[color] = Player()

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

        for num_cols in CatanConstants.tile_layout:
            row = []  # type: List[Hex]
            self._board.append(row)

            for col in range(num_cols):
                row.append(Hex(deck.pop()))

    def _get_random_tile_deck(self) -> List[str]:
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

    def _prepare_data_structures(self) -> None:
        '''Create optimized data structures for easy access to some common game data.'''
        self._create_resource_map()
        self._create_vertex_map()
        self._create_vertex_set()
        self._create_road_set()

        # this is the available set of nodes on which settlements can be built
        self.available_settlement_set = self._vertex_set.copy()
        assert len(self.available_settlement_set) > 0

        # place the robber on the desert hex
        self._find_desert_hex()
        self._robber_hex = self._desert_pos
        #self._robber_hex = self._resource_map["desert"][0]

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

    def add_road(self, v1: Vertex, v2: Vertex, color: str, initial_placement: bool = False) -> None:
        '''Add a road of the given color to the map. Charge the player for it.
        Rules:
        - (v1, v2) is not an existing road
        - at least one of (v1, v2) must connect to a same color settlement OR
        - at least one of (v1, v2) must connect to a same color road
        Road spans between v1 and v2.
        Throw exception on error'''

        v1, v2 = self._normalize_road(v1, v2)

        if not self.can_place_road(v1, v2, color):
            raise RoadPlacementError(f"Cannot place road for player {color}")

        p = self.get_player(color)
        cost = CatanConstants.building_costs["road"]

        if not initial_placement and not p.can_deduct_resources(cost):
            raise RoadPlacementError("cannot afford road")

        self._roads.add((v1, v2))
        if p.get_num_roads() >= 2:
            p.deduct_resources(cost)
        p.add_road(v1, v2)
        # now figure out whether this makes this road the longest road

        road_length = self._get_road_length(v1, color)
        if not initial_placement:
            logger.debug(f"{color}'s new road has length {road_length}")
        if ((self._longest_road_player is None and road_length >= 5) or
                (self._longest_road_player is not None and road_length > self._longest_road_length)):
            if self._longest_road_player:
                self._longest_road_player.remove_special_card("longest road")
                if self._longest_road_player != p:
                    logger.info(f"{self._longest_road_player} lost longest road card")
            p.add_special_card("longest road")
            logger.info(f"{color} now has longest road with a road length of {road_length}")
            self._longest_road_length = road_length
            self._longest_road_player = p
            logger.info(f"{p} now has longest road card")
        if initial_placement:
            logger.info(f"{color} placed a road from {v1} to {v2}")
        else:
            logger.info(f"{color} built a road from {v1} to {v2}")

    def _get_road_length(self, starting_vertex: Vertex, color: str, visited: Optional[Set[Vertex]] = None) -> int:
        '''Get the longest portion of this road starting from the given vertex'''
        if visited is None:
            visited = set([])
        visited.add(starting_vertex)
        lengths = []
        # first, find all the adjacent vertices
        player = self.get_player(color)
        for v2 in self.get_adjacent_vertices(starting_vertex):
            if v2 in visited:
                continue
            if player.has_road_to(v2):
                visited2 = visited.copy()
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

    def __end_initial_placement(self):
        '''Verify that everything has been placed and transition to another state'''
        assert self._placement_count == len(self._colors) * 2
        for color in self._colors:
            p = self._players[color]
            if p.get_num_settlements() < 2:
                raise Exception(f"{color} has fewer than 2 settlements")
            if p.get_num_roads() < 2:
                raise Exception(f"{color} has fewer than 2 roads")
        logger.debug("Initial placement succeeded, moving to new state")
        self._state = GameState.ROLL_DICE

    def can_place_settlement(self, v: Vertex) -> bool:
        assert v in self._vertex_set
        return v in self.available_settlement_set

    def __can_place_road_from_direction(self, v1: Vertex, v2: Vertex, color: str) -> bool:
        '''Only check the direction v1 -> v2'''

        if self._has_road(v1, v2):
            # logger.debug("HAS ROAD")
            return False

        player = self.get_player(color)
        if not (player.has_road_to(v1) or player.has_settlement_at(v1)):
            # have to build a road from either a settlement or another road
            # logger.debug("road from nowhere?")
            return False

        if player.has_settlement_at(v1):
            # can always build from your own settlement
            return True

        # now deal with concerning case - building from road
        # and there is a settlement of another color at v1
        return not(v1 in self._settlements and self._settlements[v1].color() != color)

    def can_place_road(self, v1: Vertex, v2: Vertex, color: str) -> bool:
        '''Note the rule here:
        https://www.catan.com/faq/6508-roads-may-i-extend-interrupted-continuous-road
        '''
        v1, v2 = self._normalize_road(v1, v2)
        if (v1, v2) in self._roads:
            # logger.debug(f"road exists: {v1} - {v2}")
            return False
        return self.__can_place_road_from_direction(v1, v2, color) or \
            self.__can_place_road_from_direction(v2, v1, color)

    def add_settlement(self, v: Vertex, color: str, initial_placement: bool = False) -> None:
        '''Add a settlement of the given color to the map.
        Deduct the cost if building is in a valid place, and if we're not in the initial placement state.
        Raise exception if cannot afford or cannot build.'''

        if not self.can_place_settlement(v):
           raise SettlementPlacementError(f"vertex {v} is not a valid spot to build a settlement")

        p = self.get_player(color)
        cost = CatanConstants.building_costs["settlement"]

        # cannot build settlements in the middle of nowhere
        if not initial_placement and not p.has_road_to(v):
            raise SettlementPlacementError(f"no road for player {color} to vertex {v}")

        if not initial_placement and not p.can_deduct_resources(cost):
            raise SettlementPlacementError(f"player {color} cannot afford settlement")

        if not initial_placement:
            p.deduct_resources(cost)

        s = Settlement(v, color)
        self._settlements[v] = s # add to the game board
        p.add_settlement(v, s) # add to player for record-keeping
        self.cull_bad_settlement_vertices(v) # make sure nothing can be built around it
        if initial_placement:
            logger.info(f"{color} placed a settlement at {v}")
        else:
            logger.info(f"{color} built a settlement at {v}")
        if initial_placement and p.get_num_settlements() == 2:
            logger.info("Producing resources from second settlement...")
            self.produce_resources_from_settlement(s)

    def get_players_on_robber_hex(self):
        '''Return a list of player colors on the hex with the robber.'''

        s = set([])

        for v in self.get_robber_hex().get_vertices():
            if v in self._settlements:
                s.add(self._settlements[v].color())

        return list(s)

    def add_city(self, v: Vertex, color: str) -> None:
        '''Add a city of the given color to the map.
        Upgrades existing settlement.
        Deduct the cost if building is in a valid place.
        Throw exception if cannot build the city'''

        p = self.get_player(color)

        if v not in self._settlements:
            raise CityUpgradeError(f"{v} not an existing settlement")

        if self._settlements[v].is_city():
            raise CityUpgradeError(f"settlement located at {v} is already a city, cannot upgrade")

        if self._settlements[v].color() != color:
            raise CityUpgradeError(f"settlement is not yours to upgrade!")

        cost = CatanConstants.building_costs["city"]
        if not p.can_deduct_resources(cost):
            raise CityUpgradeError("You cannot afford to upgrade")

        self._settlements[v].upgrade()
        p.deduct_resources(cost)
        p.upgrade_settlement_to_city(v)

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

    def produce_resources_from_settlement(self, s: Settlement, ignore_robber: bool = False) -> List[str]:
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

    def produce_resources_from_roll(self, roll: int) -> Dict[str, List[str]]:
        '''For the given roll, return a map of player color to resources produced.
        Also distribute those resources to relevant players'''
        d = {}  # type: Dict[str, List[str]]
        if roll == 7:
            return d # no resources ever produced on a seven
        for hex in self._resource_map[roll]:
            resource = hex.get_resource()
            for v in hex.get_vertices():
                if v in self._settlements:
                    s = self._settlements[v]
                    color = s.color()
                    d.setdefault(color, [])
                    if s.is_city():
                        d[color].extend([resource, resource])
                    else:
                        d[color].append(resource)
        # now add these resources to the relevant players
        for color, r_list in d.items():
            self._players[color].add_resources(r_list)
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
        # TODO: this is very sketchy because returning the main board data structure
        return self._board

    def get_state(self) -> GameState:
        return self._state

    def get_turn(self) -> int:
        return self._turn

'''Generate a map of Catan'''

#################
#    IMPORTS    #
#################
import random
from collections import deque
from catan_gen import CatanConstants
from hex import Hex
from utils import CatanUtils
from player import Player
from settlement import Settlement
from ai import AI
#from gen_board import CatanApp

class SettlementPlacementException(Exception):
    pass

class MapGen():
    '''Engine for generating Catan maps.'''

    def __init__(self):
        self._decr_set = set([1, 2, 4, 6])
        self._players = {}
        self.ai = AI(self)

    def gen(self):
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
        
    def create_players(self, colors):
        '''Create brand new players. For now, they are just placeholders.'''
        
        for c in colors:
            self._players[c] = Player()
            
    def get_player(self, color):
        '''Return the player with the given color.'''
        
        return self._players[color]

    def _assign_tokens(self):
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


    def _get_next_tile(self, row, col, unplaced_layout):
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

    def _place_tiles(self, deck):
        '''Place tiles on the board.'''

        for row_num, num_cols in enumerate(CatanConstants.tile_layout):
            row = []
            self._board.append(row)

            for col in range(num_cols):
                row.append(Hex(deck.pop()))
        
    def _make_deck(self):
        '''Return a shuffled deck of unplaced resources.'''

        deck = CatanConstants.get_resource_distribution_pool()
        random.shuffle(deck)
        return deck

    def draw_ascii(self):
        '''Render the board in a terminal.'''
        
        f = lambda hex: hex.get_token()
        
        for row in self._board:
            if len(row) == 3:
                print " ".join([f(c) for c in row])
            elif len(row) == 2:
                print " " + " ".join([f(c) for c in row]) + " "
            elif len(row) == 1:
                print (2 * " ") + f(row[0]) + (2 * " ")
                
    def prepare(self):
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
        
    def _find_desert_hex(self):
        '''Find the desert hex and set self._desert_pos to its position in the form (row, col).'''
        
        for row_i, row in enumerate(self._board):
            for col, hex in enumerate(row):
                if hex.get_resource() == "desert":
                    self._desert_pos = (row_i, col)
                    return
        
    def deduct_settlement_resources(self, player):
        '''Deduct resources for settlement construction from the given player.'''
        
        return self.deduct_resources(player, CatanConstants.building_costs["settlement"])
    
    def deduct_resources(self, player, resource_list):
        '''Deduct the given resources from the given player.'''
        
        return self._players[player].deduct_resources(resource_list)
        
    def cull_bad_settlement_vertices(self, v):
        '''Given that a settlement was built on vertex v, remove adjacent vertices from the
        set of viable building nodes for settlements. Also remove that vertex.'''
        
        adjacent_v_set = set(self.get_adjacent_vertices(v))
        self.available_settlement_set.difference_update(adjacent_v_set)
        self.available_settlement_set.discard(v)
        
    def get_nodes(self):
        return self._vertex_set
    
    def _has_road(self, v1, v2):
        '''True iff the road from v1 to v2 has been built.'''
        
        return (v1, v2) in self._roads
    
    def _road_connects_same_color_settlement(self, v1, v2, color):
        '''True iff this road connects to a settlement of the same color.'''
        
        return (v1 in self._settlements and self._settlements[v1].color() == color) or \
            (v2 in self._settlements and self._settlements[v2].color() == color)
            
    def _road_connects_same_color_road(self, v1, v2, color):
        '''True iff this road connects to another road of the same color.'''
        
        return self.get_player(color).has_road_to(v1) or self.get_player(color).has_road_to(v2)
    
    def add_road(self, v1, v2, color):
        '''Add a road of the given color to the map.
        Rules:
        - (v1, v2) is not an existing road
        - at least one of (v1, v2) must connect to a same color settlement OR
        - at least one of (v1, v2) must connect to a same color road
        Road spans between v1 and v2.'''
        
        if v1[0] > v2[0]:
            v1, v2 = v2, v1
            
        p = self.get_player(color)
        
        # first condition only applies to first 2 roads
        if self._has_road(v1, v2) or \
        not (self._road_connects_same_color_settlement(v1, v2, color) or \
        (self._road_connects_same_color_road(v1, v2, color) and \
        p.get_num_roads() >= 2)):
            return False
        else:
            self._roads.update((v1, v2))
            p.add_road(v1, v2)
            return True
        
    def has_road(self, v1, v2):
        '''Return true iff a road from v1 to v2 has already been built.
        Also allows for a road from v2 to v1'''
        
        if v1[0] > v2[0]:
            v1, v2 = v2, v1 # switch places
            
        return (v1, v2) in self._roads
        
    def add_settlement(self, v, color):
        '''Add a settlement of the given color to the map.'''
        
        if v not in self.available_settlement_set:
           return False
       
        p = self.get_player(color)
        
        # cannot build settlements in the middle of nowhere
        if p.get_num_settlements() >= 2 and not p.has_road_to(v):
            return False
        
        if v in self._vertex_set:
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
        
        for v in self.get_robber_hex.get_vertices():
            if v in self._settlements:
                s.add(self._settlements[v].color())
                
        return list(s)
            
            
    def add_city(self, v, color):
        '''Add a city of the given color to the map.
        Upgrades existing settlement.'''
        
        if v in self._settlements and not self._settlements[v].is_city() and self._settlements[v].color() == color:
            self._settlements[v].upgrade()
            return True
        else:
            return False
        
    def _create_vertex_set(self):
        '''Create a set of all vertices (nodes) on the map.
        Used in settlement placement.'''
        
        self._vertex_set = set(self._vertex_map.keys())
        
    def _create_vertex_map(self):
        ''' vertex_map maps coordinates to list of hexes 
        Used to quickly determine adjacency when settlement is placed. '''
        
        self._vertex_map = {}
        
        for row in self._board:
            for hex in row:
                for v in hex.get_vertices():
                    if v not in self._vertex_map:
                        self._vertex_map[v] = []
                    self._vertex_map[v].append(hex)

    def produce(self, s, ignore_robber=False):
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

    def get_resources_produced(self, roll):
        '''For the given roll, return a map of player color to resources produced.'''
        
        d = {}
        
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
        for p, r_list in d.iteritems():
            self._players[p].add_resources(r_list)
        
        return d

    def get_adjacent_vertices(self, v):
        '''Return all vertices adjacent to vertex v.'''
        
        adjacent_v = []
        
        # first, get tiles that v1 is a member of
        adjacent_hexes = self._vertex_map[v]
        
        # adjacent vertices are found only in adjacent tiles
        for hex in adjacent_hexes:
            v_set = hex.get_vertices()
            v_i = v_set.index(v) # we know that this exists
            # on each tile, eadjacent vertices are +1 and -1 index away
            adjacent_v.extend([v_set[v_i - 1], v_set[(v_i + 1) % len(v_set)]])
            
        return adjacent_v
    
    def _create_road_set(self):
        '''Compile a set of tuples, each of which is a valid road.'''
        
        self._road_set = set([])
        
        for v in self._vertex_set:
            v_road_set = set([(v, v2) for v2 in self.get_adjacent_vertices(v)])
            self._road_set.update(v_road_set)
            
    def get_roads(self):
        return self._road_set
    
    def robber_discard(self):
        '''Return map of color to number of resources each player must discard.'''
        
        d = {}
        
        for c, p in self._players.iteritems():
            if p.get_num_resources() > 7:
                d[c] = p.get_num_resources() // 2 # explicit integer division
            
        return d
    
    def _get_hex_at_coords(self, row, col):
        '''Return hex object at the given coordinates.'''
        
        return self._board[row][col]
                
    def get_robber_hex(self):
        '''Return the hex with the robber on it.'''
        
        #return self._robber_hex
        return self._get_hex_at_coords(*self._robber_hex)
    
    def set_robber_hex(self, row, col):
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
        
    def robber_steal(self, from_player, to_player):
        '''Robber steals from from_player and gives to to_player.
        Return the resource that was stolen.
        If from_player has no cards, return None.'''
        
        r = self._players[from_player].steal_resource()
        
        if r is not None:
           self._players[to_player].add_resources([r])
            
        return r
                
    def _create_resource_map(self):
        ''' resource_map maps numbers to list of hexes 
        Used in resource distribution when dice are rolled.'''
        
        self._resource_map = {}
        
        for row in self._board:
            for hex in row:
                if hex.get_number() is None:
                    self._resource_map["desert"] = [hex] # this will be the only entry
                    continue
                elif hex.get_number() not in self._resource_map:
                    self._resource_map[hex.get_number()] = []
                    
                self._resource_map[hex.get_number()].append(hex)
                
#        CatanUtils.print_dict(self._resource_map)
                
    def get_map(self):
        return self._board

    def draw(self):
        '''Render the board.'''

        pass
    
def gen_map():
    '''Generate a map in the map generator.
    Print ASCII representation of the map'''
    
    mg = MapGen()
    mg.gen()
    mg.prepare()
    
    print mg._road_set
    
    mg.draw_ascii()
    
if __name__ == "__main__":
    gen_map()
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
#from gen_board import CatanApp

class SettlementPlacementException(Exception):
    pass

class MapGen():
    '''Engine for generating Catan maps.'''

    def __init__(self):
        self._decr_set = set([1, 2, 4, 6])
        self._players = {}

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
            #print letters[-1]
            #print "(%d, %d)" % (col, row)
            #print unplaced_layout
            
            # withdraw a letter from the map
            if self._board[row][col].get_resource() != "desert":
                #self._board[row][col].set_token(CatanConstants.token_map[letters.pop()])
                self._board[row][col].set_token(letters.pop())
            
            unplaced_layout[row] -= 1

            if unplaced_layout[row] == 0:
                del(unplaced_layout[row])

            if len(unplaced_layout) > 0:
                row, col = self._get_next_tile(row, col, unplaced_layout)


    def _get_next_tile(self, row, col, unplaced_layout):
        # calculate next tile position
        if row <= min(unplaced_layout.keys()) - 1 and col >= 0:
            # reverse direction
            #print "changing direction"
            col = -1 * col - 1
        elif row >= max(unplaced_layout.keys()) + 1 and col < 0:
            col = (1 + col) * -1

        if col >= 0:
            row -= 1
        elif col < 0:
            row += 1

        if row == 2 and col >= 0:
            col += 1

        if row in unplaced_layout:
            return (row, col)
        else:
            return self._get_next_tile(row, col, unplaced_layout)

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
        
        for row in self._board:
            if len(row) == 3:
                print " ".join([c.get_resource() for c in row])
            elif len(row) == 2:
                print " " + " ".join([c.get_resource() for c in row]) + " "
            elif len(row) == 1:
                print (2 * " ") + row[0].get_resource() + (2 * " ")
                
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
        
    def get_nodes(self):
        return self._vertex_set
    
    def add_road(self, v1, v2, color):
        '''Add a road of the given color to the map.
        Road spans between v1 and v2.'''
        
        if (v1 not in self._settlements and v2 not in self._settlements) or \
           (v1 in self._settlements and self._settlements[v1][1] != color) or \
           (v2 in self._settlements and self._settlements[v2][1] != color):
            return False
        else:
            self._roads.update((v1, v2))
            return True
        
    def add_settlement(self, v, color):
        '''Add a settlement of the given color to the map.'''
        
        #TODO first do a check if close to another settlement
        adjacent_v_set = self.get_adjacent_vertices(v)
        
        for adjacent_v in adjacent_v_set:
            if adjacent_v in self._settlements:
                return False
        
        if v in self._vertex_set:
            self._settlements[v] = ("s", color)
            return True
        else:
            return False
            
    def add_city(self, v, color):
        '''Add a city of the given color to the map.
        Upgrades existing settlement.'''
        
        if v in self._settlements and self._settlements[v] == ("s", color):
            self._settlements[v] = ("c", color)
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
                    
#        CatanUtils.print_dict(self._vertex_map)

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
                    
                    if s[1] not in d:
                        d[s[1]] = []
                    
                    if s[0] == "c":
                        d[s[1]].extend([r, r])
                    else:
                        d[s[1]].append(r)
                        
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
                
    def _create_resource_map(self):
        ''' resource_map maps numbers to list of hexes 
        Used in resource distribution when dice are rolled.'''
        
        self._resource_map = {}
        
        for row in self._board:
            for hex in row:
                if hex.get_number() is None:
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
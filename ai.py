import random

class AI():
    
    def __init__(self, board):
        self._board = board
        
    def get_random_road_from_settlement(self, v):
        '''Return a random road stemming from settlement located at v.'''
        
        for v2 in self._board.get_adjacent_vertices(v):
            if not self._board.has_road(v, v2):
               return (v, v2) # the road was built
           
        return False # no road can be built from this settlement
        
    def get_random_settlement(self):
        '''Return a valid settlement placement.'''
        
        # randomly pick a valid vertex to place a settlement
        v = random.choice(list(self._board.available_settlement_set))
        return v
        
    def get_random_road(self, color):
        '''Return a valid road placement for the given player.
        This placement is chosen at random.'''
        
        # pick a random settlement to start the road from
        player = self._board.get_player(color)
        nexi = [player.get_settlement(i) for i in range(player.get_num_settlements())]
        random.shuffle(nexi)
        
        # if I made 
        while len(nexi) > 0:
            s = nexi.pop()
            v1 = s.vertex()
            
            for v2 in self._board.get_adjacent_vertices(v1):
                if not self._board.has_road(v1, v2):
                   return (v1, v2) # the road was built
               
        # cycled through all possible settlement-road combinations and could not find valid placement
        return False
    
    
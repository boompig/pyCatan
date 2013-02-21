'''
The model, which keeps track of game state
@author: dan
'''

class Model():
    states = [
        "first settlement placement",
        "first road placement",
        "second settlement placement",
        "second road placement",
        "additional settlement placement", # for when a third+ settlement is built
        "additional road placement", # for when a third+ road is built
        "city improvement", # NOT the C&K raw city placement
        "robber movement", 
        "normal game_play" # anything other than above
    ]
             
    
    def __init__(self, board, player_map, player_order):
        '''The board should be... IDK... 
        The player_order should be list of colors'''
        
        self._board = board
        self._player_map = player_map
        self._players = player_order
        self._state = 0 # first state
        self._turn = 0 # first player
        
    def next_turn(self):
        self._turn = (self._turn + 1) % len(self._players)
        
    def add_settlement(self, v, color):
        '''Add a settlement. Deal with state changes.'''
        
        #TODO actually add the settlement
        # TODO here need to evaluate if there should be a change of state
        
        # note that the settlement placement must be during settlement placement phase
        if self.states[self._state] == "additional settlement placement":
            #TODO check that the settlement is connected to previously existing road
            self._state = len(self.states) - 1
        else:
            if self._players.index(color) == len(self._players) - 1:
                self._state += 1
            else:
                self.next_turn()
    
    def add_city(self, v, color):
        pass
    
       
    
    def add_road(self, v1, v2, color):
        '''Add a road. Deal with state changes.'''
        
        # TODO add the road
        
        pass
        if self.states[self._state] != "additional road placement":
            if self._players.index(color) == len(self._players) - 1:
                self._state += 1
            else:
                self.next_turn()
    


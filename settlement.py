class Settlement():
    '''Representation for a city or settlement.'''
    
    def __init__(self, v, color):
        '''Create a new settlement of given color at given vertex.'''
        
        self._v = v
        self._c = color
        self._city = False
        
    def is_city(self):
        '''Return True iff this settlement is actually a city.'''
        
        return self._city
    
    def upgrade(self):
        '''Upgrade this settlement to a city.'''
        
        self._city = True
        
    def vertex(self):
        '''Return the vertex at which this city/settlement is placed.'''
        
        return self._v
    
    def color(self):
        '''Return the color of this city/settlement.'''
        
        return self._c
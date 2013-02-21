'''This will render all map objects.'''

from utils import CatanUtils
from Tkinter import HIDDEN

# given a map, render it
class CatanRender():
    
    
    
    @staticmethod
    def draw_settlement_node(canvas, v, d):
        #print v
        
        padding = 10
        canvas.create_oval(
           v[0] - padding,
           v[1] - padding,
           v[0] + padding,
           v[1] + padding, 
           tags="settlement_oval",
           fill="", # transparent fill
           outline="" # no outline
        )
        
        # curry the function
        d[v] = lambda e: CatanRender.settle_call(e, v)
        canvas.tag_bind("settlement_oval", "<Button>", func=d[v])
        pass
        
    @staticmethod
    def settle_call(event, v):
        print "making settlement at {}".format(v)
        print "({}, {})".format(event.x, event.y)
        
if __name__ == "__main__":
    pass
'''I use this file to test GUI elements before putting them in gen_board.
Here is a prototype of a God Window, responding to events triggered in the game window.

TODO create sprites for arrows'''

from Tkinter import *
from catan_gen import CatanRenderConstants
import random
from player import Player
from utils import CatanUtils

class App():
    width = 800
    height = 400
    
    colors = ["red", "green", "blue"]
    
    def __init__(self, root):
        self._root = root
        
        self.create_models()
        self.create_widgets()
        
    def create_down_arrow(self):
        pass
        
    def create_widgets(self):
        '''Create all Tkinter widgets on start.'''
        
        self._canvas = None
        
        self._root.title("Game Window")
        self._game_window = Frame(root, width=self.width, height=self.height)
        self._game_window.pack()
        
        self._god_window =  Toplevel()
        self._god_window.title("God Window")
        
        self._discard_window =  Toplevel()
        self._discard_window.title("Discard Window")
        
        self.create_game_window()
        self.create_god_window()
        self.create_discard_window()
        
    def create_discard_window(self):
        self._discard_canvas = Canvas(self._discard_window, width=App.width, height=App.height)
        self._discard_canvas.pack()
        
        c = self._canvas
        self._canvas = self._discard_canvas
        self.draw_down_arrow(0, 0)
        
        if c is not None:
            self._canvas = c
        
    def draw_down_arrow(self, x_offset, y_offset):
        
        self._canvas.create_polygon(
            *CatanUtils.get_tkinter_coords(self.get_down_arrow_coords()),
            fill="red",
            tag="down_arrow"
        )
        
    def get_down_arrow_coords(self):
        return ((5, 0),
                (15, 0),
                (15, 20),
                (20, 20),
                (10, 30),
                (0, 20),
                (5, 20))
        
    def create_game_window(self):
        
        roll_button = Button(self._game_window, text="Roll", command=self.roll)
        roll_button.pack()
        
        self._roll_var = StringVar()
        roll_label = Label(self._game_window, textvariable=self._roll_var)
        roll_label.pack()
    
    def create_god_window(self):
        
        self._god_canvas = Canvas(self._god_window, width=App.width, height=App.height)
        self._god_canvas.pack()
        
        temp = self._canvas
        self._canvas = self._god_canvas
        
        for c in self.colors:
            self.draw_top_resource_bar(c)
            
        if temp is not None:
            self._canvas = temp
        
    def create_models(self):
        '''Create all models on start.'''
        
        self.resources = CatanRenderConstants.resource_color_map.keys()
        self.create_players()
        
    def create_players(self):
        self._players = {}
        
        for c in self.colors:
            self._players[c] = Player()
        
    def roll(self):
        n = random.randint(1, 6)
        
        self._roll_var.set(str(n))
        
        if n == 6:
            print "No resources"
        else:
            r = self.resources[n - 1]
            print "Giving 2 {} to each player".format(r)
            
            for c, p in self._players.iteritems():
                p.add_resources([r] * 2)
                self.draw_update_hand(c)
                
    def draw_update_hand(self, color):
        '''Update the hand of the player with given color.'''
        
        hand = self._players[color].get_hand()
        for r, count in hand.iteritems():
            item = self._canvas.find_withtag("god_hand_count_{}_{}".format(color, r))
            self._canvas.itemconfigure(item, text=str(count))
        # update the associated model        
        
    def get_resource_box_coords(self, resource_text_coords):
        '''Return bounding coordinates for resource box in top resource bar given its label's coordinates.'''
        
        x, y = resource_text_coords
        return (x - 52, y - 15, x - 12, y + 15)
    
    def get_resource_number_coords(self, resource_box_coords):
        return ((resource_box_coords[0] + resource_box_coords[2]) / 2,
                (resource_box_coords[1] + resource_box_coords[3]) / 2)
        
    def draw_top_resource_bar(self, color):
        
        self._canvas.create_rectangle(
            50, 
            self.colors.index(color) * 100 + 10,
            90,
            self.colors.index(color) * 100 + 50,
            fill=color,
            width=1.5
        )
        
        rect = self._canvas.create_rectangle(
          140, 
          5 + self.colors.index(color) * 100, 
          App.width, 
          60 + self.colors.index(color) * 100, 
          fill="burlywood3", 
          outline="black", 
          width=1.5
        )
        
        # now resource labels and rectangles
        x_incr = 130
        x_offset = 200
        
        for i in range(5):
            resource = self.resources[i]
            r_text_coords = (x_offset + i * x_incr, 35 + self.colors.index(color) * 100)
            r_box_coords = self.get_resource_box_coords(r_text_coords)
            r_num_coords = self.get_resource_number_coords(r_box_coords)
            
            self._canvas.create_text(
                *r_text_coords,
                text=resource,
                justify=LEFT,
                anchor=W,
                font=("Helvetica", 14)
            )
            
            self._canvas.create_rectangle(
              *r_box_coords,
              fill=CatanRenderConstants.resource_color_map[resource],
              width=1.5
            )
            
            self._canvas.create_text(
                *r_num_coords,
                text="0",#str(n),
                tag="god_hand_count_{}_{}".format(color, resource),
                font=("Helvetica", 14)
            )
        
if __name__ == "__main__":
    root = Tk()
    a = App(root)
    root.mainloop()
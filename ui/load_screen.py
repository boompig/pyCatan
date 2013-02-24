from Tkinter import *
from ui_constants import UIConstants

class LoadScreen(Canvas):
    '''The loading screen for the game
    '''
    
    # window size
    HEIGHT = 400
    WIDTH = 600
    
    # configuration for color selection
    COLOR_CHOICE_RECT_SIZE = 50
    COLOR_CHOICE_RECT_PADDING = 20
    
    # configuration for number of players
    MIN_NUM_PLAYERS = 3
    MAX_NUM_PLAYERS = 4
    NUM_PLAYER_PADDING = 20
    
    # positions on screen
    GAME_LOGO_ORIGIN = (200, 100)
    COLOR_CHOICE_ORIGIN = (300, 230)
    NUM_PLAYER_CHOICE_ORIGIN = (100, 230)
    DEBUG_ORIGIN = (300, 350)
    
    def __init__(self, master, debug_flag=False):
        Canvas.__init__(self, master)
        
        # actually useful stuff
        self._player_color = UIConstants.PLAYER_COLORS[0]
        self._num_players = self.MIN_NUM_PLAYERS
        self._debug = debug_flag
        if self._debug: self._debug_var = StringVar()
        
        # garbage AKA GUI
        self.config(height=self.HEIGHT, width=self.WIDTH)
        self.create_ui()
        
    def create_ui(self):
        '''Create loading screen UI.'''
        
        self.create_color_choice()
        self.create_num_player_choice()
        self.create_logo()
        
        if self._debug:
            self.create_debug_window()
        
    def create_logo(self):
        '''Put game logo on the screen.'''
        
        #TODO create a better logo
        l = Label(self, text="Settlers of Catan")
        l.pack()
        self.create_window(*self.GAME_LOGO_ORIGIN, window=l)
        
    def create_debug_window(self):
        '''Create a window and a variable especially for debugging.'''
        
        
        debug_label = Label(self, textvar=self._debug_var)
        debug_label.pack()
        
        self.create_window(*self.DEBUG_ORIGIN, window=debug_label)
        
    def create_num_player_choice(self):
        '''Create interface to choose number of players.'''
        
        label = Label(self, text="Number of players")
        label.pack()
        self.create_window(*self.NUM_PLAYER_CHOICE_ORIGIN, window=label)
        
        num_player_choice = IntVar()
        f = lambda: self.select_num_players(num_player_choice.get())
        for i, num in enumerate(range(self.MIN_NUM_PLAYERS, self.MAX_NUM_PLAYERS + 1)):
            
            b = Radiobutton(self, 
                            text=str(num)+" players", 
                            variable=num_player_choice, 
                            value=num,
                            command=f)
            b.pack()
            self.create_window(self.NUM_PLAYER_CHOICE_ORIGIN[0], self.NUM_PLAYER_CHOICE_ORIGIN[1] + self.NUM_PLAYER_PADDING * (i + 1), window=b)
            
            # make sure to select the relevant button :)
            if num == self._num_players:
                b.select()
    
    def select_num_players(self, number):
        '''Select number of players.'''
        
        if number != self._num_players:
            self._num_players = number
            
            if self._debug:
                self._debug_var.set("Number of players is now %d" % number)
    
    def create_color_choice(self):
        '''Create the interface to choose player color.'''
        
        color_choice_label = Label(self, text="Choose a color:")
        color_choice_label.pack()
        
        for i, color in enumerate(UIConstants.PLAYER_COLORS):
            self.create_color_choice_rect(
              self.COLOR_CHOICE_ORIGIN[0] + i * LoadScreen.COLOR_CHOICE_RECT_SIZE + (i + 1) * LoadScreen.COLOR_CHOICE_RECT_PADDING, 
              self.COLOR_CHOICE_ORIGIN[1], 
              color
            )
            
        self.create_window(*self.COLOR_CHOICE_ORIGIN, window=color_choice_label, anchor=E)
        
        # invoke the command associated with default one
        self.select_color(self._player_color)
        
    def select_color(self, color):
        '''A color was clicked. Make that the player selection color.'''
        
        # disable previous selection
        if self._player_color is not None:
            item = self.find_withtag(self.get_color_choice_rect_tag(self._player_color))
            self.itemconfig(item, width=1)
        
        # change pref
        self._player_color = color
        if self._debug:
            self._debug_var.set(self._player_color)
        
        # reflect that change in the GUI
        item = self.find_withtag(self.get_color_choice_rect_tag(color))
        self.itemconfig(item, width=4)
        
    def get_color_choice_rect_tag(self, color):
        '''Return custom tag for the rectangle in the given color.'''
        
        return "color_choice_rect_%s" % color
            
    def create_color_choice_rect(self, x, y, color):
        '''Create rectangle for color choice.'''
        
        t = self.get_color_choice_rect_tag(color)
        
        self.create_rectangle(
          x,
          y, 
          x + LoadScreen.COLOR_CHOICE_RECT_SIZE,
          y + LoadScreen.COLOR_CHOICE_RECT_SIZE,
          fill=color,
          tags=("color_choice_rect", t),
          outline="black",
          width=1
        )
        
        f = lambda event: self.select_color(color)
        self.tag_bind(t, "<Button-1>", f)
        
class CatanGame(Frame):
    '''Main frame to contain settlers of catan game.'''
    
    TITLE = "Settlers of Catan: Buxom Wenches Expansion"
    
    STATES = [
        "LOAD_SCREEN"
    ]
    
    def __init__(self, master, debug=True):
        Frame.__init__(self, master)
        self.focus_set()
        self.master.title(self.TITLE)
    
        # set 
        self._canvas = LoadScreen(self, debug)
        self._canvas.pack()
    
def play_game():
    '''Play Catan!'''
    
    # set some variables...
    
    
    # create the window
    root = Tk()
    
    #TODO add some properties so it's always on top, or something?
    # turn debugging on
    frame = CatanGame(root, True)
    frame.pack()
    
    # start the app
    root.mainloop()
    
if __name__ == "__main__":
    play_game()
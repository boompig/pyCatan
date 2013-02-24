from Tkinter import *
import random
import time

class Hole():
	def __init__(self, points):
		self._p = points
	
	def points(self):
		return self._p
		
	def process_ball(self):
		print "Scored {} points!".format(self._p)

class Sample():
	def __init__(self, root):
		self._root = root
		self._hole_dict = {}
		
		self._canvas = Canvas(self._root, width=800, height=500)
		self._canvas.pack()
		
		self._drag_data = {"x" : 0, "y" : 0, "item" : None}
		
		self.draw_holes()
		self._draw_ball((100, 100))
		
		
	def draw_holes(self):
		for i in range(5):
			p = (random.randint(400, 700), i * 100 + 50)
			model = Hole(p[0])
			hole_sprite = self._draw_hole(p, model)
			self._hole_dict[hole_sprite] = model
		
	def _draw_hole(self, center, model):
		#t = ("hole")#, "hole_at_{}_{}".format(center[0], center[1]))
	
		hole_sprite = self._canvas.create_oval(
			center[0] - 40,
			center[1] - 40,
			center[0] + 40,
			center[1] + 40,
			fill="red",
			tags="hole"
		)
		
		self._canvas.create_text(
			*center,
			text=str(model.points()),
			fill="white"
		)
		
		return hole_sprite
		
	def _draw_ball(self, center):
		self._ball = self._canvas.create_oval(
			center[0] - 25,
			center[1] - 25,
			center[0] + 25,
			center[1] + 25,
			fill="blue",
			activefill="yellow",
			tags="ball"
		)
		
		self._canvas.tag_bind("ball", "<ButtonPress-1>", self.on_ball_click)
		self._canvas.tag_bind("ball", "<B1-Motion>", self.on_ball_drag)
		self._canvas.tag_bind("ball", "<ButtonRelease-1>", self.on_ball_release)
		
		
	def on_ball_click(self, event):
		'''Process button event when user clicks mouse on top of ball.'''
	
		self._drag_data["item"] = self._ball
		self._drag_data["x"] = event.x
		self._drag_data["y"] = event.y
		#self._canvas.itemconfigure(self._ball, status=ACTIVE)	
	
	def on_ball_drag(self, event):
		dx = event.x - self._drag_data["x"]
		dy = event.y - self._drag_data["y"]
		
		self._canvas.move(self._drag_data["item"], dx, dy)
		
		self._drag_data["x"] = event.x
		self._drag_data["y"] = event.y

	def on_ball_release(self, event):
		'''Process button event when user releases mouse holding ball.'''

		# reset the drag data
		self._drag_data = {"x" : 0, "y" : 0, "item" : None}
		
		# use small invisible rectangle and find all overlapping items
		items = self._canvas.find_overlapping(event.x - 10, event.y - 10, event.x + 10, event.y + 10)
		
		for item in items:
			# there should only be 1 overlapping hole
			if "hole" in self._canvas.gettags(item):
				hole = self._hole_dict[item]
				hole.process_ball()
				
	def move_ball(self, new_x, new_y, old_x, old_y):
		
		self._canvas.move(self._ball, new_x - old_x, new_y - old_y)
			
if __name__ == "__main__":
	root = Tk()
	s = Sample(root)
	root.mainloop()
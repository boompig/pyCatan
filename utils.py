def to_tkinter_coords(coords, top, offset=(0, 0)):
	t = None
	
	for coord in coords:
		t_new = (coord[0] + offset[0], top - coord[1] - offset[1])
	
		if t is None:
			t = t_new
		else:
			t = t + t_new
	
	return t
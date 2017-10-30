import wx
def draw_rect(grid, attr, dc, rect):
	"""Draws a rect"""
	dc.SetBrush(wx.Brush(wx.Colour(15, 255, 127), wx.SOLID))
	dc.SetPen(wx.Pen(wx.BLUE, 1, wx.SOLID))
	dc.DrawRectangleRect(rect)
def draw_bmp(bmp_filepath):
	"""Draws bitmap"""
	def draw(grid, attr, dc, rect):
		bmp = wx.EmptyBitmap(100, 100)
		try:
			dummy = open(bmp_filepath)
			dummy.close()
			bmp.LoadFile(bmp_filepath, wx.BITMAP_TYPE_ANY)
			dc.DrawBitmap(bmp, 0, 0)
		except:
			return
	return draw
def draw(draw_func):
	"""Executes the draw function"""
	return draw_func

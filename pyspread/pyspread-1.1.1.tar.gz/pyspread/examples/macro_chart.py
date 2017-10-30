
import guidata
from guiqwt.plot import CurveDialog
from guiqwt.builder import make

_app = guidata.qapplication()

def hist(data):
	"""Plots histogram"""
	
	win = CurveDialog(edit=False, toolbar=True, wintitle="Histogram test")
	plot = win.get_plot()
	plot.add_item(make.histogram(data))
	win.show()
	win.exec_()
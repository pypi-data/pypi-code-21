from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import scipy.signal as sps, scipy.ndimage as spi
x = np.linspace(-10, 10, 1000)
y = 5*np.sin(2*x**2)/x
app = QtGui.QApplication([])
pg.setConfigOptions(antialias=True,background='w')
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
win = pg.GraphicsWindow(title="Basic plotting examples")
#win.resize(800,600)
#win.setWindowTitle('pyqtgraph example: Plotting')



p4 = win.addPlot(title="Parametric, grid enabled")
p4.plot(x, y,pen=(255,0,0))
p4.showGrid(x=True, y=True)
## Switch to using white background and black foreground
p4.setLabel('left', "Y Axis", units='A')
p4.setLabel('bottom', "Y Axis", units='s')
p4.setLogMode(x=True, y=False)
raw_input("continue")
p4.plot(x, y**2,pen=(255,0,0))


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
        pg.QtGui.QApplication.exec_()

    
    

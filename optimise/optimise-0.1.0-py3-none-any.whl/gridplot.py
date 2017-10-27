import matplotlib as mpl
import matplotlib.pyplot as plt
from importlib import reload


class Gridplot(object):
    """ decorates plt functions to show multiple charts in a grid
        useful in jupyter for neater output
    """

    def __init__(self, rows=20, cols=4, width=4, height=4):
        """ parameters are size of grid and plots """
        self.rows = rows
        self.cols = cols
        self.index = 1
        mpl.rcParams['figure.figsize'] = (self.cols*width, self.rows*height)
        reload(plt)

        # decorate the plt functions
        plt.plot = self.plot_decorator(plt.plot)
        plt.bar = self.plot_decorator(plt.bar)
        plt.hist = self.plot_decorator(plt.hist)
        plt.scatter = self.plot_decorator(plt.scatter)
        plt.imshow = self.plot_decorator(plt.imshow)

        self.on = self.__init__

    def plot_decorator(self, func):
        """ wraps plot with autoincrementing subplot """
        def decorated(*args, **kwargs):
            plt.subplot(self.rows, self.cols, self.index)
            self.index = self.index + 1
            if self.index > self.rows * self.cols:
                plt.show()
                self.index = 1
            return func(*args, **kwargs)
        return decorated

    def off(self):
        reload(plt)

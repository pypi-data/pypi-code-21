from threading import Thread
from time import sleep
from curses import KEY_RESIZE, ungetch
from .Win import *

class WProgress(Win, Thread):
    def __init__(self, *args, **kwargs):
        """ Creates a progress bar window, which displays and ASCII progress bar
        proportionnal to a value, regularly checked.

        Special optionnal arguments are :

        function -- the function, called regularly, returning the proportion of
                    the bar that should be filled (between 0 and 1) or None if 
                    this thread must stop
        delay    -- delay between each function call
        barchar  -- character used to draw the bar
        """
        Thread.__init__(self, daemon=True)
        self.function = kwargs.pop('function', lambda : 0)
        self.delay    = kwargs.pop('delay', 1)
        self.barchar  = kwargs.pop('barchar', '=')
        Win.__init__(self, *args, **kwargs)
        self.last_val = 0

    def refresh(self, update=True, get_root_lock=True):
        if self.borders:
            self.window.border(*self.borders)
        if 0 <= self.last_val <= 1:
            bar = self.barchar * int(self.line_length * self.last_val)
            bar += ' ' * (self.line_length - len(bar))
            self.window.addstr(1, 1, bar)
        Win.refresh(self, update, get_root_lock)

    def run(self):
        while self.last_val != None:
            prev = self.last_val
            self.last_val = self.function()
            if self.last_val == None:
                return
            if self.last_val != prev:
                self.refresh()
            sleep(self.delay)

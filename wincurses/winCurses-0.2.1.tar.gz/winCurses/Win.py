import curses
from threading import Lock

class Coord:
    def __init__(self, y, x):
        """ Creates a couple of coordinates (y,x) which can be a boolean, or an
        iterable of 2 booleans. The 2nd boolean indicates if the coordinate is
        relative to the parent (True), in which case the coordinate will be 
        between 0 and 1, or absolute (should be an integer)
        """
        x = ((x, False) if '__iter__' not in x.__dir__() else x)
        y = ((y, False) if '__iter__' not in y.__dir__() else y)
        self.y, self.relative_y = y
        self.x, self.relative_x = x

    def absolutize(self, parent_size):
        """ return the corresponding absolute Coords

        parent_size -- the Coord of the parent window, in order to convert
                       relative coordinates
        """
        # Absolutize
        abs_y = int((self.y * parent_size.y) if self.relative_y else self.y)
        abs_x = int((self.x * parent_size.x) if self.relative_x else self.x)

        # Positivize
        abs_y = (abs_y if abs_y >= 0 else parent_size.y + abs_y)
        abs_x = (abs_x if abs_x >= 0 else parent_size.x + abs_x)

        return(Coord(abs_y, abs_x))

    def yx(self):
        """ Returns a (y,x) couple of coordinates """
        return((self.y, self.x))

    def copy(self):
        """ Returns an exact copy of self """
        return(Coord((self.y, self.relative_y), (self.x, self.relative_x)))

    def __str__(self):
        """ A human-friendly way to display coordinates """
        rel2txt = lambda x : ('REL' if x else 'ABS')
        return("(%f[%s], %f[%s])" % (self.y, rel2txt(self.relative_y), self.x, rel2txt(self.relative_x)))

class Win:
    def __init__(self, parent=None, pos=None, dim=None, layer=0, borders=None):
        """ Creates a simple Window, without content

        parent  -- parent window; if None, this window will be considered as
                   root window and will try to initialize a curses window
        pos     -- Coord describing the position of the top left corner
        dim     -- Coord describing the size of the window
        layer   -- integer describing the layer, default is 0, windows with 
                   highest layers will be on foreground (but remember that
                   children are always drawn on top of parents)
        borders -- borders array, or None if no borders
        """
        if not parent:
            self.window  = curses.initscr()
            self.pos     = Coord(0,0)
            self.dim     = Coord(*self.window.getmaxyx())
            self.parent  = None
            self.root    = self
            self.layer   = layer
            self.borders = None
            self.focus   = None
            self._lock   = Lock()
            curses.noecho()
            if curses.has_colors():
                curses.start_color()
                curses.init_pair(curses.COLOR_WHITE, curses.COLOR_WHITE, curses.COLOR_BLACK)
                curses.init_pair(curses.COLOR_MAGENTA, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
                curses.init_pair(curses.COLOR_BLUE, curses.COLOR_BLUE, curses.COLOR_BLACK)
                curses.init_pair(curses.COLOR_CYAN, curses.COLOR_CYAN, curses.COLOR_BLACK)
                curses.init_pair(curses.COLOR_GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
                curses.init_pair(curses.COLOR_RED, curses.COLOR_RED, curses.COLOR_BLACK)
                curses.init_pair(curses.COLOR_YELLOW, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        else:
            self.parent   = parent
            self.root     = parent.root
            self.borders  = borders
            self.pos      = (pos if pos else self.parent.pos.copy())
            self.dim      = (dim if dim else Coord(1.0, 1.0, True))
            self.layer    = layer
            self.parent.children.append(self)
            self.parent.children.sort(key=lambda c:c.layer)
            self.create_window()
        
        self.max_lines, self.line_length = self.get_content_dim().yx()
        self.children = []

    def __del__(self):
        for child in self.children:
            del child

        if self.parent:
            self.parent.children.remove(self)
        else:
            curses.endwin()

    def create_window(self):
        """ Creates the associated curses window """
        cur_pos = self.pos.absolutize(self.parent._get_dim())
        cur_dim = self.dim.absolutize(self.parent._get_dim())
        
        self.window = curses.newwin(*cur_dim.yx(), *cur_pos.yx())
        if self.borders:
            self.window.border(*self.borders)

    def resize(self):
        """ Resizes the windows after recalculating its dimensions """
        if not self.parent:
            self.dim = Coord(*self.window.getmaxyx())

        cur_pos = self.pos.absolutize(self.parent._get_dim()) if self.parent else self.pos
        cur_dim = self.dim.absolutize(self.parent._get_dim()) if self.parent else self.dim

        self.window.resize(*cur_dim.yx())
        if self.parent:
            self.window.mvwin(*cur_pos.yx())
        self.max_lines, self.line_length = self.get_content_dim().yx()
        for child in self.children:
            child.resize()

    def clear(self, refresh=False):
        """ Clears the windows and redraw borders

        refresh -- if True, window will be refreshed after cleaning
        """
        self.window.clear()
        if self.borders:
            self.window.border(*self.borders)
        if refresh:
            self.refresh(True)

    def refresh(self, update=True, get_root_lock=True):
        """ Refreshed this window and all its children

        update        -- indicates if we have to update the screen
        get_root_lock -- must it wait for the root lock, or is it already
                         launched by a thread-safe parent refresh
        """
        if get_root_lock:
            self.root._lock.acquire() # Wait for the root lock

        self.window.noutrefresh()
        for child in self.children:
            child.refresh(False, False)
        if update:
            # Updates the focused windows at last, to give it focus
            if self.root.focus:
                self.root.focus.refresh(False, False)
            curses.doupdate()

        if get_root_lock:
            self.root._lock.release()

    def _get_dim(self):
        return(Coord(*self.window.getmaxyx()))

    def get_content_dim(self):
        """ Returns the internal dimensions of the windows, ie size without
        border. Even if no borders are drawn, a "marging" will be kept
        """
        dim = self._get_dim()
        dim.y -= 2
        dim.x -= 2
        return(dim)


def convert_color(color):
    """ Converts a color in the corresponding curses value, if curses has colors
    enabled
    
    color -- a curses color (curses.COLOR_*)
    """
    if not curses.has_colors():
        return(0)
    return(curses.color_pair(color))

import curses as crs
import curses.panel as panel
import shutil

colors = { 'black'       : (1, crs.COLOR_BLACK),
           'blue'        : (2, crs.COLOR_BLUE),
           'cyan'        : (3, crs.COLOR_CYAN),
           'green'       : (4, crs.COLOR_GREEN),
           'magenta'     : (5, crs.COLOR_MAGENTA),
           'red'         : (6, crs.COLOR_RED),
           'white'       : (7, crs.COLOR_WHITE),
           'yellow'      : (8, crs.COLOR_YELLOW) } 

class Frame(object):
    
    def __init__(self, name: str) -> None:
        self._cols, self._lines = shutil.get_terminal_size()
        self.name = name
        self.color = 'black'
        try:
            self._curses_init()
            self._curses_color()
        except:
            pass

    def _curses_init(self):
        self._win = crs.newwin(self._lines, self._cols)
        self._pan = panel.new_panel(self._win)
        self._curses_color()

    def _curses_color(self):
        crs.init_pair(colors[self.color][0], 
                      crs.COLOR_BLACK, 
                      colors[self.color][1])
        self._win.bkgd(crs.color_pair(colors[self.color][0]))

    def setcolor(self, color: str) -> None:
        self.color = color
        try:
            self._curses_color()
        except:
            pass

    def hide(self) -> None:
        self._pan.hide()
        self._win.refresh()

    def show(self) -> None:
        self._pan.show()
        self._win.refresh()


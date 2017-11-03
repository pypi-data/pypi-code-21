
from Tkinter import Tk

from _base import BaseWindow
from ..mixin.menubar import MenuBarMixIn


class RootWindow(BaseWindow,
                 MenuBarMixIn,
                 Tk):

    def __init__(self,
                 *args,
                 **kwargs):

        Tk.__init__(self)
        super(RootWindow, self).__init__(*args, **kwargs)

        self.mainloop()

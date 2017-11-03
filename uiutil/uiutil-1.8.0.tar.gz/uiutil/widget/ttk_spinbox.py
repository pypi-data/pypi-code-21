
import ttk


class Spinbox(ttk.Widget):
    def __init__(self, master, **kw):
        ttk.Widget.__init__(self, master, 'ttk::spinbox', kw)

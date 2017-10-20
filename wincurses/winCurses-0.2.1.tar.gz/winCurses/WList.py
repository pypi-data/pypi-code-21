from .Win import *

class WList(Win):
    def __init__(self, *args, **kwargs):
        Win.__init__(self, *args, **kwargs)
        self.list = []

    def append(self, value):
        if type(value) not in [list, tuple]:
            value = (value, 0)
        self.list.append(self, value)
        self.refresh()

    def __delitem__(self, value):
        self.list.__delitem__(self, value)
        self.refresh()

    def remove(self, value):
        if type(value) not in [list, tuple]:
            value = (value, 0)
        self.list.remove(self, value)
        self.refresh()

    def load(self, new_list):
        self.list = new_list
        self.refresh()

    def refresh(self, update=True, get_root_lock=True):
        self.clear()
        inner_dim = self.get_content_dim()
        for i in range(min(inner_dim.y - 1, len(self.list))):
            self.window.addstr(i+1, 1, self.list[i][0][:inner_dim.x], convert_color(self.list[i][1]))
        if len(self.list) > inner_dim.y:
            self.window.addstr(inner_dim.y, 1, "...")

        Win.refresh(self, update, get_root_lock)

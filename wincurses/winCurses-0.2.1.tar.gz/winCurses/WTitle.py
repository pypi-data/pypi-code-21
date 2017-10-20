from .Win import *

class WTitle(Win):
    def __init__(self, *args, **kwargs):
        self.title = kwargs.pop('title', '')
        Win.__init__(self, *args, **kwargs)

    def set_title(self, t, refresh=True):
        self.title = t
        if refresh:
            self.refresh()

    def refresh(self, update=True, get_root_lock=True):
        self.clear()

        y_offset = int(self._get_dim().y / 2)
        x_offset = int((self._get_dim().x - len(self.title)) / 2) if len(self.title) < self.get_content_dim().x else 1
        self.window.addstr(y_offset, x_offset, self.title[:self.get_content_dim().x])
        Win.refresh(self, update, get_root_lock)

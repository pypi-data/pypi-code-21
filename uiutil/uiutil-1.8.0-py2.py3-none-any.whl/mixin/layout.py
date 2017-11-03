
import ttk

from ..helper.layout import nice_grid, get_centre
from stateutil.incrementor import Incrementor


class LayoutMixIn(object):

    def __init__(self,
                 *args,
                 **kwargs):

        super(LayoutMixIn, self).__init__()

    def modal_window(self,
                     window):

        window.transient()
        window.grab_set()
        self.wait_window(window)

    def nice_grid(self,
                  *args,
                  **kwargs):
        nice_grid(self, *args, **kwargs)

    def nice_grid_rows(self,
                       *args,
                       **kwargs):
        nice_grid(self, columns=False, *args, **kwargs)

    def nice_grid_columns(self,
                          *args,
                          **kwargs):
        nice_grid(self, rows=False, *args, **kwargs)

    def get_centre(self):
        return get_centre(geometry=self.winfo_geometry())

    def get_parent_centre(self):
        return get_centre(geometry=self.parent_geometry)

    def get_screen_centre(self):
        return get_centre(x=(self.winfo_screenwidth() / 2),
                          y=(self.winfo_screenheight() / 2),
                          width=self.width,
                          height=self.height)


class FrameLayoutMixIn(LayoutMixIn):

    def __init__(self,
                 *args,
                 **kwargs):

        super(LayoutMixIn, self).__init__()

        self.row = Incrementor()
        self.column = Incrementor()

        self.grid(row=self._grid_row,
                  column=self._grid_column,
                  padx=self._grid_padx,
                  pady=self._grid_pady,
                  columnspan=self._grid_columnspan,
                  rowspan=self._grid_rowspan)

    def _set_title(self, title):
        if isinstance(self, ttk.LabelFrame):
            self.config(text=title)

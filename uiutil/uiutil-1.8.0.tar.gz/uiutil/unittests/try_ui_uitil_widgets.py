
import logging_helper; logging = logging_helper.setup_logging()

from Tkconstants import NORMAL, DISABLED, HORIZONTAL, E, W, EW, CENTER

from stateutil.incrementor import Incrementor
from uiutil.window.root import RootWindow
from uiutil.frame.frame import BaseFrame
from uiutil.widget.entry import TextEntry, IntEntry


class SuperWidgetFrame(BaseFrame):
    def __init__(self,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

        self.TEXT_FIELD_WIDTH = 23
        self.BUTTON_WIDTH = 20

        self.__add_widgets()

    def __add_widgets(self):

        self.grid(sticky=EW)

        self.text_entry = TextEntry(
            frame=self,
            state=NORMAL,
            width=self.BUTTON_WIDTH,
            trace=self.text,
            row=self.row.next(),
            tooltip=u"Some tooltip text")

        self.int_entry = IntEntry(
            frame=self,
            state=NORMAL,
            width=self.BUTTON_WIDTH,
            trace=self.int,
            row=self.row.next(),
            tooltip=u"Some other tooltip text")

        self.nice_grid()

    def text(self):
        print u"text"
        print self.text_entry.value

    def int(self):
        print u"int"
        print self.int_entry.value


class StandaloneSuperWidgetFrame(RootWindow):

    def __init__(self, *args, **kwargs):
        super(StandaloneSuperWidgetFrame, self).__init__(*args, **kwargs)

    def _setup(self):
        __row = Incrementor()
        __column = Incrementor()

        self.title(u"Test Super Widgets Frame")

        self.sw = SuperWidgetFrame(parent = self._main_frame,
                                   grid_row = __row.next(),
                                   grid_column = __column.current)

if __name__ == u'__main__':
    StandaloneSuperWidgetFrame(width = 650, height = 400)

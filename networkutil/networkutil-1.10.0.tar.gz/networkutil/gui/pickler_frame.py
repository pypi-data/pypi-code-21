import logging_helper; logging = logging_helper.setup_logging()

import better_exceptions
from Tkconstants import NORMAL, DISABLED, HORIZONTAL, E, W, EW, CENTER, NSEW
import pyperclip
import requests
import pickle
from stateutil.incrementor import Incrementor
from uiutil.window.root import RootWindow
from uiutil.frame.frame import BaseFrame
from uiutil.window.child import ChildWindow
from uiutil.widget.button import Button
from uiutil.widget.entry import TextEntry
from uiutil.widget.label import Label


class RequestPicklerFrame(BaseFrame):
    def __init__(self,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

        self.grid(sticky=EW)

        Label(text=u'Pickler:',
              width=10,
              sticky=W)

        Label(text=u'URI:',
              width=10,
              sticky=W,
              row=self.row.next())

        self.uri = TextEntry(frame=self,
                             width=50,
                             column=self.column.next(),
                             sticky=EW,
                             tooltip=u"Enter the url of the request you'd like to pickle")

        Button(state=NORMAL,
               text=u"Pickle",
               width=8,
               sticky=EW,
               column=self.column.next(),
               command=self.pickle_uri_and_copy_to_clipboard,
               tooltip=u'Pickle the request and\n'
                       u'copy the pickled string\n'
                       u'to the clipboard.')

        self.nice_grid()

    def pickle_uri_and_copy_to_clipboard(self):
        try:
            pyperclip.copy(pickle.dumps(requests.get(self.uri.value)))
        except Exception as e:
            pass
            # TODO: Show dialog

    def cancel(self):
        self.parent.master.exit()


class RequestPicklerWindow(ChildWindow):

    def __init__(self,
                 *args,
                 **kwargs):

        super(RequestPicklerWindow, self).__init__(*args, **kwargs)

    def _setup(self):
        self.title(u"Request Pickler")

        self.config = RequestPicklerFrame(parent=self._main_frame)
        self.config.grid(sticky=NSEW)

    #def close(self):
    #    self.config.cancel()


class StandaloneRequestPicklerFrame(RootWindow):
    def __init__(self, *args, **kwargs):
        super(StandaloneRequestPicklerFrame, self).__init__(*args, **kwargs)

    def _setup(self):
        __row = Incrementor()
        __column = Incrementor()

        self.title(u"Test Pickler Frame")

        RequestPicklerFrame(parent=self._main_frame,
                            grid_row=__row.next(),
                            grid_column=__column.current)


if __name__ == u'__main__':
    StandaloneRequestPicklerFrame(width=500, height=150)


from Tkconstants import NONE, RIGHT, Y, HORIZONTAL, BOTTOM, X, LEFT, BOTH
from Tkinter import Text, Scrollbar
from base_widget import BaseWidget
from ..frame.frame import BaseFrame
from ..frame.introspection import locate_calling_base_frame
from ..helper.arguments import pop_kwarg, raise_on_positional_args, get_grid_kwargs, get_widget_kwargs


class TextScroll(BaseWidget):

    """
    TextScroll made of a frame, with optional scroll bars contanining a Text
    object. The Text object methods are available idrectly, as well as BaseWidget's.
    The other objects (hbar, vbar, containing_frame) can also be accessed,
    e.g. text_scroll_instance.hbar
    """

    WIDGET = Text
    VAR_TYPE = u'string_var'
    VAR_PARAM = u'textvariable'

    def __init__(self,
                 # frame=None,
                 # vbar=True,
                 # hbar=True,
                 *args,
                 **kwargs):

        raise_on_positional_args(self, args)
        frame = pop_kwarg(kwargs, u'frame')
        vbar = pop_kwarg(kwargs, u'vbar', True)
        hbar = pop_kwarg(kwargs, u'hbar', True)

        frame = locate_calling_base_frame(frame)

        grid_kwargs = get_grid_kwargs(frame=frame,
                                      **kwargs)

        widget_kwargs = get_widget_kwargs(**kwargs)

        # Setup a containing frame
        self.containing_frame = BaseFrame(frame,
                                          grid_padx=0,
                                          grid_pady=0)
        kwarg_upd = {u'wrap': NONE}

        if vbar:
            self.vbar = Scrollbar(self.containing_frame)
            self.vbar.pack(side=RIGHT, fill=Y)
            kwarg_upd[u'yscrollcommand'] = self.vbar.set

        if hbar:
            self.hbar = Scrollbar(self.containing_frame, orient=HORIZONTAL)
            self.hbar.pack(side=BOTTOM, fill=X)
            kwarg_upd[u'xscrollcommand'] = self.hbar.set

        widget_kwargs.update(kwarg_upd)

        super(TextScroll, self).__init__(frame=self.containing_frame,
                                         **widget_kwargs)

        self.widget.pack(side=LEFT, fill=BOTH, expand=True)

        if vbar:
            self.vbar[u'command'] = self.widget.yview

        if hbar:
            self.hbar[u'command'] = self.widget.xview

        self.containing_frame.grid(**grid_kwargs)

    def __str__(self):
        return str(self.containing_frame)

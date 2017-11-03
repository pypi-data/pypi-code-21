
import ttk


class StyleMixIn(object):

    def __init__(self,
                 *args,
                 **kwargs):

        super(StyleMixIn, self).__init__()

        # TODO: Is this style actually used anywhere?
        style = ttk.Style()
        style.configure(u"ActiveRow.TRadiobutton", foreground=u"blue")
        style.configure(u"ActiveRow.TButton", foreground=u"blue")
        style.configure(u"ActiveRow.TLabel", foreground=u"blue")

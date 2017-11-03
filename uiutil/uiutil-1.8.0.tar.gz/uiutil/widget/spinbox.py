from ttk_spinbox import Spinbox as ttk_spinbox
from base_widget import BaseWidget


class Spinbox(BaseWidget):
    WIDGET = ttk_spinbox
    VAR_TYPE = u'int_var'
    VAR_PARAM = u'textvariable'
    VAR_IS_OPTIONAL = False

    def __init__(self,
                 *args,
                 **kwargs):
        super(Spinbox, self).__init__(*args,
                                      **kwargs)

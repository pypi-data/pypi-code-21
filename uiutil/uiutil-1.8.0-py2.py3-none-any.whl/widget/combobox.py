import ttk
from base_widget import BaseWidget, READONLY


class Combobox(BaseWidget):
    WIDGET = ttk.Combobox
    VAR_TYPE = u'string_var'
    VAR_PARAM = u'textvariable'
    VAR_IS_OPTIONAL = False

    def __init__(self,
                 # enabled_state=READONLY,
                 *args,
                 **kwargs):
        # Default enabled state is readonly.
        # That prevents editing, which seems
        # to be the most common case for a
        # Combobox.
        kwargs[u'enabled_state'] = kwargs.get(u'enabled_state', READONLY)
        kwargs[u'state'] = kwargs.get(u'state', kwargs[u'enabled_state'])
        super(Combobox, self).__init__(*args, **kwargs)

    @property
    def values(self):
        return self.widget[u'values']

    @values.setter
    def values(self,
               values):
        self.config(values=values)

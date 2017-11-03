from logging_helper import setup_logging; logging = setup_logging()

from Tkinter import NORMAL, DISABLED, TclError
from PIL import Image, ImageTk

from ..mixin import WidgetMixIn, VarMixIn
from ..frame.introspection import locate_calling_base_frame
from ..helper.arguments import pop_kwarg, raise_on_positional_args

READONLY = u'readonly'


class BaseWidget(WidgetMixIn,
                 VarMixIn):

    # Define WIDGET when subclassing.
    # It should be a ttk widget, e.g ttk.Button
    #
    # Define VAR_TYPE when subclassing.
    # It should be a VarMixIn type, e.g self.string_var
    #
    # Define VAR_PARAM when subclassing.
    # It should be the parameter name into WIDGET that takes the variable, e.g. textvariable

    VAR_IS_OPTIONAL = True

    def __init__(self,
                 # frame=None,
                 # initial_value=None,
                 # trace=None,
                 # link=None,
                 # bind=None,
                 # allow_invalid_values=True,
                 # image=None
                 # enabled_state=NORMAL
                 *args,
                 **kwargs):
        """
        No positional args are allowed.
        
        When subclassing, if validation is required, just add a staticmethod
        called validate that returns a Boolean and optionally a method called
        permit_invalid_value
        
        e.g.
        @staticmethod
        def validate(value):
            try:
                return 0 <= value <= 1000
            except:
                pass
            return False
            
        @staticmethod
        def permit_invalid_value(value):
            return len([c for c in value if c not in u'0123456789:ABCDEFabcdef']) == 0
        
        :param frame: Add the widget to this frame.
                      If not supplied, the nearest BaseFrame or BaseLabelFrame
                      in the stack will be used.
        :param initial_value: The initial value of the variable associated with the
                              widget.  If this is not supplied, then no variable is
                              created. Use the underlying widget's parameter to set
                              a static value (e.g. text for a Label)
        :param trace: function to trigger when the variable is modified
        :param link: a persistent object that the variable will link to
        :param bind: bindings for the widget. This can be a list of bindings or a single binding.
                     Each binding must be a tuple. ("event", function)
        :param allow_invalid_values
        :param image
        :param enabled_state: default is NORMAL, can be set to other values such as 'readonly',
                              which is useful in some cases.
        :param args: NO POSITIONAL ARGS ARE ALLOWED
        :param kwargs: Parameters to pass to add_widget_and_position
        """

        try:
            self.WIDGET
        except AttributeError:
            raise NotImplementedError(u'WIDGET must be defined')

        try:
            self.VAR_TYPE
        except AttributeError:
            raise NotImplementedError(u'VAR_TYPE must be defined')

        try:
            self.VAR_PARAM
        except AttributeError:
            raise NotImplementedError(u'VAR_PARAM must be defined')

        raise_on_positional_args(self, args)

        frame = pop_kwarg(kwargs, u'frame')
        initial_value = pop_kwarg(kwargs, u'initial_value')
        bindings = pop_kwarg(kwargs, u'bind')
        self.enabled_state = pop_kwarg(kwargs, u'enabled_state', NORMAL)
        self.allow_invalid_values = pop_kwarg(kwargs, u'allow_invalid_values', True)

        if not initial_value:
            try:
                initial_value = self.DEFAULT_VALUE
            except AttributeError:
                pass

        super(BaseWidget, self).__init__(parent=frame, **kwargs)

        self.containing_frame = locate_calling_base_frame(frame)

        self.create_variable(initial_value=initial_value,
                             kwargs=kwargs)

        self.create_widget(kwargs)
        self.copy_methods_of_underlying_widgets()
        self.add_bindings(bindings)
        self.register_validation()

    def create_variable(self,
                        initial_value,
                        kwargs):

        trace = pop_kwarg(kwargs, u'trace')
        link = pop_kwarg(kwargs, u'link')

        if not self.VAR_IS_OPTIONAL or initial_value is not None:
            # Declare the var
            var_type = getattr(self, self.VAR_TYPE)
            self.var = var_type(trace=trace,
                                link=link,
                                value=initial_value)

            kwargs[self.VAR_PARAM] = self.var

    def create_widget(self,
                      kwargs):

        self._command = pop_kwarg(kwargs, u'command')
        if self._command:
            kwargs[u'command'] = self.do_command

        image = pop_kwarg(kwargs, u'image')
        size = pop_kwarg(kwargs, u'size')
        if image:
            if isinstance(image, basestring):
                image = Image.open(image)
            if size:
                try:
                    image = image.resize(size)
                except Exception as e:
                    e
            image = ImageTk.PhotoImage(image)
            self.image = image
            kwargs[u'image'] = self.image

        if kwargs.get(u'tooltip') is not None:
            self.widget, self.tooltip = self.containing_frame.add_widget_and_position(
                                            widget=self.WIDGET,
                                            frame=self.containing_frame,
                                            **kwargs)
        else:
            self.widget = self.containing_frame.add_widget_and_position(
                              widget=self.WIDGET,
                              **kwargs)

    @property
    def has_tooltip(self):
        try:
            return bool(self.tooltip)
        except AttributeError:
            return False

    def set_cursor(self,
                   state=u""):
        try:
            self.config(cursor=state)
        except TclError:
            # Associated widget has probably been destroyed
            pass

    def do_command(self,
                   *args,
                   **kwargs):
        # Auto close tooltips on action

        if self.has_tooltip:
            self.tooltip.close()

        self.set_cursor(u"wait")
        try:
            self._command(*args, **kwargs)
        except Exception as e:
            self.set_cursor()
            logging.exception(e)
            raise e
        self.set_cursor()

    def copy_methods_of_underlying_widgets(self):
        widget_unbound_method_names = [method
                                       for method in dir(self.WIDGET)
                                       if not method.startswith(u'_') and method not in dir(self)]

        for method in widget_unbound_method_names:
             setattr(self, method, getattr(self.widget, method))

    def add_bindings(self,
                     bindings):
        if bindings:
            if not isinstance(bindings, list):
                bindings = [bindings]
            try:
                for binding in bindings:
                    if not isinstance(binding, tuple):
                        raise ValueError(u"Each binding in the list must be a tuple."
                                         u" e.g. (u'<Return>', self._bound_function)")
                    self.bind(*binding)

            except AttributeError as e:
                raise RuntimeError(u'Underlying widget does not have a bind method')

    def register_validation(self):
        try:
            self.valid
            self.widget[u'validate'] = u"key",
            self.widget[u'validatecommand'] = (self.widget.register(self.do_validation), u"%P")
        except AttributeError:
            pass  # no validation

    def do_validation(self,
                      new_value):
        # Allow a blank, otherwise it prevents deletion to the start of the field
        if new_value.strip() == u"":
            return True

        new_value_is_valid = self.valid(new_value)
        result = True if self.permit_invalid_value(new_value) else new_value_is_valid

        if result:
            self.config(foreground=u'black' if new_value_is_valid else u'red')

        return result

    def permit_invalid_value(self,
                             value):
        return self.allow_invalid_values

    @property
    def value(self):
        try:
            return self.var.get()
        except AttributeError:
            raise RuntimeError(u'No variable was declared for this widget.')

    @value.setter
    def value(self,
              value):
        try:
            self.var.set(value)
        except AttributeError:
            raise RuntimeError(u'No variable was declared for this widget.')

    def enable(self):
        self.widget.config(state=self.enabled_state)

    def disable(self):
        self.widget.config(state=DISABLED)


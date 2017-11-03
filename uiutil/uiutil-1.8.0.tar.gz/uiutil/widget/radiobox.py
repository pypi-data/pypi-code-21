from Tkinter import EW, NORMAL, DISABLED
from collections import OrderedDict

from ..mixin import VarMixIn, ObserverMixIn, WidgetMixIn
from ..frame.label import BaseLabelFrame
from ..frame.introspection import locate_calling_base_frame
from ..helper.arguments import pop_kwarg, pop_mandatory_kwarg, raise_on_positional_args, get_grid_kwargs


class RadioBox(VarMixIn,
               WidgetMixIn,
               ObserverMixIn):
    # TODO: Add max_rows/max_columns, same behaviour as SwitchBox
    def __init__(self,
                 # title,
                 # options,
                 # frame=None,
                 # options=None,
                 # command=None,
                 # option_parameters=None,
                 # link=None,
                 # width=None,
                 # sort=True,
                 # take_focus=None,
                 *args,
                 **kwargs):
        """
        There's small leap to make with labels versus objects.
        Objects can be anything hashable, which the option is associated with
        and the labels are the strings displayed. If just labels are supplied,
        the labels are used as the associated objects (This is likely to be the
        most common usage).

        Getting the state of a switch uses the associated object as a key,
        not the label (unless they're the same)

        :param title: Text for the label frame
        :param options: A list of option labels or, if the option objects
                        and labels are different, a dictionary:

                                  {"label": <switch object>,
                                   ...
                                   "label": <switch object>}

        :param option_states: Dictionary of initial switch states, these values
                              also override persisted states. Not all objets
                              need to be in this list, so if you always want
                              to set a subset of the switches, this is where
                              you do it. Dict looks like this:

                                  {<switch object>: <switch state>,
                                    ...
                                   <switch object>: <switch state>}

        :param link: A Persist object (or subclass). A dictionary is stored that 
                     uses the labels as keys. This is because they're strings,
                     which are easier to store than objects

        :param switch_parameters: Parameters for the individual switches, e.g.:

                                  {<switch object>: {"tooltip", "Switch for the thing"},
                                    ...
                                   <switch object>: {"tooltip", "Switch for another thing"}}
        :param width: 
        :param args: invalid. positional args are poison in BaseWidget!
        :param kwargs:
        """

        self.initialising = True

        raise_on_positional_args(self, args)
        frame = pop_kwarg(kwargs, u'frame', locate_calling_base_frame())
        title = pop_mandatory_kwarg(kwargs, u'title')
        options = pop_mandatory_kwarg(kwargs, u'options')
        self.command = pop_kwarg(kwargs, u'command')
        option_parameters = pop_kwarg(kwargs, u'option_parameters', {})
        self.link = pop_kwarg(kwargs, u'link')
        width = pop_kwarg(kwargs, u'width')
        sort = pop_kwarg(kwargs, u'sort', True)
        take_focus = pop_kwarg(kwargs, u'take_focus')

        grid_kwargs = get_grid_kwargs(frame=frame,
                                      **kwargs)

        # All other kwargs are discarded.

        super(RadioBox, self).__init__(*args, **kwargs)

        # Setup a containing frame
        self.containing_frame = BaseLabelFrame(frame)

        self.containing_frame._set_title(title=title)

        # Set up object to label mapping...

        if not isinstance(options, dict):
            # Only label labels, so make a dictionary
            # using those labels as the objects
            temp = OrderedDict()

            for option in options:
                # key=label: value=label (labels and objects are the same)
                temp[option] = option

            options = temp

        if sort:
            options = OrderedDict(sorted(options.items(),
                                         key=lambda t: t[0]))

        self.options = {}

        self.var = self.string_var(link=self.link,
                                   value=None if self.link else options.keys()[0])

        for label, option_object in options.iteritems():

            option_params = option_parameters.get(option_object, {})

            if take_focus is not None and u'takefocus' not in option_params:
                option_params.update({u'takefocus': take_focus})

            self.options[option_object] = self.containing_frame.radiobutton(
                                               text=label,
                                               variable=self.var,
                                               value=option_object,
                                               state=NORMAL,
                                               command=self._state_change,
                                               column=self.containing_frame.column.start(),
                                               width=width,
                                               sticky=EW,
                                               **option_params)
            self.containing_frame.row.next()

        self.containing_frame.grid(**grid_kwargs)

    def _state_change(self,
                      dummy=None):
        if self.link:
            self.link.value = self.value
        self.notify_observers()

    @property
    def selected(self):
        return self.value

    @property
    def value(self):
        return self.var.get()

    @value.setter
    def value(self,
              value):
        self.var.set(value)

    def enable(self,
               option=None):
        if option is None:
            for option in self.options.values():
                option.config(state=NORMAL)
        else:
            option.config(state=NORMAL)

    def disable(self,
                option=None):
        if option is None:
            for option in self.options.values():
                option.config(state=DISABLED)
        else:
            option.config(state=DISABLED)

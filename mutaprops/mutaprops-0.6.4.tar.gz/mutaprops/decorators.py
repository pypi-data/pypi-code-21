#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from .mutaprops import MutaProperty, MutaAction, MutaPropClass, MutaSource

logger = logging.getLogger(__name__)


def mutaprop_class(display_name, gui_id=None, gui_major_version=0,
                   gui_minor_version=0):
    """ Class-level decorator. It is required for classes whose instances should
    be visible for the Mutaprop UI manager.

    :param display_name: Class name/description to be accessible by the UI API.
                         In most cases, it's not really important.
    :param gui_id:       API-level identifier of a class definition.
                         In most cases, it's not really important.
    :param gui_major_version:  Reserved for future use.
    :param gui_minor_version:  Reserved for future use.
    """

    def decorator(cls):
        logger.debug("Registered mutaprop class: %s", cls.__name__)
        return type("MutaProp{0}".format(cls.__name__), (cls, MutaPropClass),
                    {MutaPropClass.muta_attr(MutaPropClass.MP_NAME):
                         display_name,
                     MutaPropClass.muta_attr(MutaPropClass.MP_GUI_ID): gui_id,
                     MutaPropClass.muta_attr(
                         MutaPropClass.MP_GUI_MAJOR_VERSION): gui_major_version,
                     MutaPropClass.muta_attr(
                         MutaPropClass.MP_GUI_MINOR_VERSION): gui_minor_version,
                     "__doc__": cls.__doc__,
                     "_orig_cls": cls})

    return decorator


def mutaproperty(display_name, value_type, **kwargs):
    """ Create a UI property out of existing attribute.

    :param display_name:  A name to be displayed at the UI level.

    :param value_type:  [:class:`~mutaprops.mutaprops.MutaTypes`]

    Optional arguments - general

    :param read_only:  bool, dynamic_
                       Sets GUI element to read-only state. Automatically
                       set to true when setter is not defined.

    :param select:  :class:`list` or :class:`dict`, dynamic_
                    Set of allowed values. GUI will offer just this set.

                    If it's :class:`list`, the list items must conform to the
                    `value_type`::

                        @mutaproperty("Cheese", MutaTypes.STRING,
                                      select=['Stilton', 'Gruyere', 'Liptauer'])
                        def cheese(self):
                            return self._cheese

                    If it's :class:`dict`, the keys will be displayed as
                    a selector view, and the values will be set::

                        @mutaproperty("Cheese", MutaTypes.INT,
                                      select={'Stilton': 1, 'Gruyere': 2,
                                              'Liptauer': 3})
                        def cheese(self):
                            return self._cheese

    :param priority:  int
                      Display priority, higher numbers are displayed first

    :param hierarchy:  string
                       Hierarchy path in the GUI. MutaProps with the same
                       hierarchy patch are grouped together.

    :param deford:  int
                    Modifies definition order. This is normally defined
                    automatically based on the decorator calls.
                    If priority is not used, the order at which
                    MutaProps are listed in GUI is defined by deford.

    Optional arguments - numerical type (`MutaTypes.INT`, `MutaTypes.REAL`)

    :param min_val:  int, dynamic_
                     Minimum possible value,

    :param max_val:  int, dynamic_
                     Maximum possible value,

    :param step:  int, dynamic_
                  For numerical type, step interval between values,
                  for other types ignored

    Optional arguments - `MutaTypes.STRING`

    :param min_val:  int, dynamic_
                     Minimal length of string

    :param max_val:  int, dynamic_
                     Maximal length of string

    Optional arguments - `MutaTypes.BOOL`

    :param toggle:  Dict of format::

                        {'on': 'Some-on-label',
                         'off': 'Some-off-label'}

                    If set, a toggle-switch like control will be used
                    as GUI instead of a simple checkbox.

    .. _dynamic:

    **Dynamic arguments**

    Where dynamic argument is supported, the value doesn't have to be only
    a class definition constant, but also another
    :class:`~mutaprops.mutaprops.MutaProp` or
    :class:`~mutaprops.mutaprops.MutaSource`.

    Dynamic arguments can be referred only directly and cannot be in any sort
    of expression, as this expression is evaluated only once during
    the class definition time::

        @mutaproperty("Some useful flag", MutaTypes.BOOL)
        def some_flag(self):
            return self._some_flag

        @some_flag.setter
        def some_flag(self, value):
            self._some_flag = value

        @mutaproperty("Ham", MutaTypes.STRING,
                      read_only=some_flag)  # direct referral, will work
        def ham(self):
            return self._spam

        @mutaproperty("Spam", MutaTypes.STRING,
                      read_only=not some_flag)  #expression, will not work
        def spam(self):
            return self._spam
    """

    def decorator(func):
        logger.debug("Registered mutaproperty: %s", func.__name__)
        kwargs[MutaProperty.MP_FGET] = func
        prop = MutaProperty(func.__name__, display_name, value_type, **kwargs )
        return prop
    return decorator


def mutasource(func=None, class_scope=False):
    """ Decorated attribute's changes will be notified to the UI layer, but
        will not be displayed.

        MutaSource allows to implement some additional controller (as in MVC)
        logic in addition to the usual mutaproperties. Usually used to
        enable or disable (read_only) some parts of UI depending on other
        parameters, or change the select values.

    :param class_scope:  [True, False]
                         Set to reflect class-level attribute.
    """
    if func:
        logger.debug("Registered mutasource: %s", func.__name__)
        return MutaSource(func.__name__, None, None,  fget=func,
                          class_scope=False)
    else:
        def decorator(fget):
            logger.debug("Registered mutasource: %s", fget.__name__)
            return MutaSource(fget.__name__, None, None,
                              class_scope=class_scope, fget=fget)
        return decorator


def mutaprop_action(display_name, **kwargs):
    """ Make decorated method accessible in the UI.

    :param display_name:  A name to be displayed at the UI level.

    :param read_only:  bool, dynamic_
                       Sets GUI element to read-only state. Automatically
                       set to true when setter is not defined.

    :param priority:  int
                      Display priority, higher numbers are displayed first

    :param hierarchy:  string
                       Hierarchy path in the GUI. MutaProps with the same
                       hierarchy patch are grouped together.

    :param deford:  int
                    Modifies definition order. This is normally defined
                    automatically based on the decorator calls.
                    If priority is not used, the order at which
                    MutaProps are listed in GUI is defined by deford.
    """

    def decorator(func):
        logger.debug("Registered mutaprop action: %s", func.__name__)
        action = MutaAction(func.__name__, display_name, func, **kwargs)
        return action
    return decorator

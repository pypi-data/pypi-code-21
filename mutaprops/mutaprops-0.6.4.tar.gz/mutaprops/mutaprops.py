#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum
import logging
import types
from collections import OrderedDict
from .utils import MutaPropError, rest_to_html

logger = logging.getLogger(__name__)


class MutaTypes(Enum):
    """ Representation of allowed MutaProperty types.
    """
    STRING = 0
    INT = 1
    REAL = 2
    BOOL = 3
    HTML = 4

    @classmethod
    def typecast(cls, muta_type, string_value):
        """ Cast string representation of the value to the particular
            python type.
        """

        if muta_type == cls.STRING:
            return string_value
        elif muta_type == cls.INT:
            return int(string_value)
        elif muta_type == cls.REAL:
            return float(string_value)
        elif muta_type == cls.BOOL:
            return bool(string_value.lower() == 'true')
        elif muta_type == cls.HTML:
            return string_value
        else:
            raise MutaPropError("Unknown value type {0}".format(muta_type))


class MutaProp(object):
    """ Abstract class defining a generic MutaProp object.
        Such object holds basic information about a "property" of a
        MutaProp-accessible class (such as ID and human-readable name)
        as well as position of such property in the hierarchy of all properties.

        Each MutaProp implementation is expected to overload following:
         * :meth:`~mutaprops.MutaProp._allowed_kwargs` class method,
            defining kwargs which are used/allowed in the constructor.
         * :meth:`~mutaprops.MutaProp._exported_kwargs` class method, i
            defining which parameters are exported during serialization
            of the MutaProp.
         * :const:`~mutaprops.MutaProp.MP_CLASS_TYPE` constant defining
            the MutaProp class for GUI use (the utilization of this parameter
            is GUI-implementation-dependent).
    """

    __definition_counter = 0
    MP_ID = 'id'    # ID of the prop (usually matches the property name)
    MP_NAME = 'name'  # Human-readable name
    MP_PRIORITY = 'priority'  # GUI display priority
    MP_HIERARCHY = 'hierarchy'  # Hierarchy position of a prop
    MP_DEFINITION_ORDER = 'deford'  #  Definition order for default ordering
    MP_DOC = 'doc'  # Prop's docstring
    MP_VIEW = 'view'  # Alternative view widget assignment where applicable
    MP_TYPE = 'type'  # Type of the Prop (Property/Action/Source)

    MP_CLASS_TYPE = 'abstract'

    # I'm using classmethods instead of class constants because of easier
    # inheritance
    @classmethod
    def _allowed_kwargs(cls):
        """ Define kwargs which are allowed in the constructor."""
        return cls.MP_PRIORITY, cls.MP_HIERARCHY, cls.MP_DEFINITION_ORDER, \
               cls.MP_DOC, cls.MP_VIEW

    @classmethod
    def _exported_params(cls):
        """ Define which parameters are exported/serialized to the GUI"""
        return (cls.MP_ID, cls.MP_NAME, cls.MP_PRIORITY, cls.MP_HIERARCHY,
                cls.MP_DEFINITION_ORDER,  cls.MP_DOC, cls.MP_VIEW, cls.MP_TYPE)

    def __init__(self, pid, display_name, **kwargs):
        """
        :param pid:  Mutaprop identifier
        :param display_name:  Mutaprop name to be displayed in GUI
        :param kwargs:  Optional attibutes
            *  `priority` : int
                            Display priority, higher numbers are displayed first
            * `hierarchy` : string
                            Hierarchy path in the GUI
            * `deford` :    int
                            Modifies definition order. This is normally defined
                            automatically based on the decorator calls.
                            If priority is not used, the order at which
                            MutaProps are listed in GUI is defined by deford.
            * `view` :      string
                            identifier of recommended GUI view type
        """
        self._muta_id = pid
        self._muta_name = display_name

        # Check for invalid kwargs
        for key in kwargs.keys():
            if key not in self._allowed_kwargs():
                raise MutaPropError("Invalid argument {0}".format(key))

        # Assign with defaults
        self._muta_priority = kwargs.get(self.MP_PRIORITY, None)

        self._muta_hierarchy = kwargs.get(self.MP_HIERARCHY, None)
        self._muta_view = kwargs.get(self.MP_VIEW, None)
        self._muta_deford = kwargs.get(self.MP_DEFINITION_ORDER, None)

        if self._muta_deford is None:
            self._muta_deford = MutaProp.__definition_counter
            MutaProp.__definition_counter += 1

        self.__doc__ = kwargs.get(self.MP_DOC, None)

    def _assign_kwarg(self, kwarg_key, kwarg_value):
        """ Converts

        :param kwarg_key:
        :param kwarg_value:
        :return:
        """
        if kwarg_key in self._allowed_kwargs():
            if kwarg_key == 'doc':
                self.__doc__ = kwarg_value
            else:
                setattr(self, "_muta_{0}".format(kwarg_key), kwarg_value)
        else:
            raise MutaPropError("Invalid keyword {0}".format(kwarg_key))

    @property
    def prop_id(self):
        return self._muta_id

    @property
    def display_name(self):
        return self._muta_name

    @property
    def display_priority(self):
        return self._muta_priority

    @property
    def hierarchy(self):
        return self._muta_hierarchy

    @property
    def view(self):
        return self._muta_view

    @property
    def definition_order(self):
        return self._muta_deford

    def __str__(self):
        temp = (
            "ID: {pid}: {name}\n" +
            "order: {deford}, priority: {priority}, hierarchy: {hierarchy}\n" +
            "Description: {doc}").format(pid=self._muta_id,
                                         name=self._muta_name,
                                         deford=self._muta_deford,
                                         priority=self._muta_priority,
                                         hierarchy=self._muta_hierarchy,
                                         doc=self.__doc__)
        return temp

    def to_dict(self, obj=None):
        temp = {}
        for attr in self._exported_params():
            if attr == self.MP_DOC:
                # Docstring is here converted from reST to HTML
                temp[self.MP_DOC] = rest_to_html(self.__doc__)
            elif attr == self.MP_TYPE:
                temp[self.MP_TYPE] = self.MP_CLASS_TYPE
            else:
                temp[attr] = MutaSource.serialize(
                                        getattr(self, '_muta_{0}'.format(attr)))

        return temp


class MutaProperty(MutaProp):
    """Emulate PyProperty_Type() in Objects/descrobject.c"""

    # Value limits and step
    MP_MAXVAL = 'max_val'
    MP_MINVAL = 'min_val'
    MP_STEP = 'step'

    MP_FGET = 'fget'  # Getter function
    MP_FSET = 'fset'  # Setter function
    MP_FDEL = 'fdel'  # Deleter function
    MP_CHANGE_CALLBACK = 'change_callback'  # Callback called on change

    MP_VALUE = 'value'  # Value of the MutaProperty
    MP_VALUE_TYPE = 'value_type'  # Type of the value (INT/BOOL...)
    MP_READ_ONLY = 'read_only'  # GUI Read only setting
    MP_SELECT = 'select'  # Iterable set of possible values
    MP_TOGGLE = 'toggle'  # GUI setting for toggle-switch representation

    MP_CLASS_TYPE = 'property'

    @classmethod
    def _allowed_kwargs(cls):
        return super()._allowed_kwargs() + (cls.MP_MAXVAL, cls.MP_MINVAL,
                                            cls.MP_STEP, cls.MP_FGET,
                                            cls.MP_FSET, cls.MP_FDEL,
                                            cls.MP_CHANGE_CALLBACK,
                                            cls.MP_SELECT, cls.MP_TOGGLE,
                                            cls.MP_READ_ONLY)

    @classmethod
    def _exported_params(cls):
        return super()._exported_params() + (cls.MP_MINVAL, cls.MP_MAXVAL,
                                             cls.MP_STEP, cls.MP_READ_ONLY,
                                             cls.MP_VALUE_TYPE,
                                             cls.MP_SELECT, cls.MP_TOGGLE)

    def __init__(self, pid, display_name, value_type, **kwargs):
        """
        :param pid:  Mutaprop identifier
        :param display_name:  Mutaprop name to be displayed in GUI
        :param value_type:  MutaType value
        :param kwargs:  Optional attibutes
            *  `priority` : int
                            Display priority, higher numbers are displayed first
            * `hierarchy` : string
                            Hierarchy path in the GUI
            * `deford` :    int
                            Modifies definition order. This is normally defined
                            automatically based on the decorator calls.
                            If priority is not used, the order at which
                            MutaProps are listed in GUI is defined by deford.
            * `view` :      string
                            identifier of recommended GUI view type
            * `min_val` :   int
                            For numerical type, minimum possible value,
                            for string type, minimal length of string
            * `max_val` :   int
                            For numerical type, maximum possible value,
                            for string type, maximal length of string
            * `step` :      int
                            For numerical type, step interval between values,
                            for other types ignored
            * `fget` :      function
                            Getter function
            * `fset` :      function
                            Setter function
            * `fdel` :      function
                            Deleter function
            * `read_only` : bool
                            Sets GUI element to read-only state. Automatically
                            set to true when setter function is not provided.
            * `select` :    List or Dict
                            Set of allowed values. GUI will offer just this set.
            * `toggle` :    Dict of format {'on': 'Some-on-label',
                                            'off': 'Some-off-label'}
                            If set, a toggle-switch like control will be used
                            as GUI. Valid only for BOOL types, otherwise
                            ignored.
        """

        doc = kwargs.get(self.MP_DOC, None)
        fget = kwargs.get(self.MP_FGET, None)

        if doc is None and fget is not None:
            kwargs[self.MP_DOC] = fget.__doc__

        super().__init__(pid, display_name, **kwargs)

        self._muta_value_type = value_type
        self._muta_min_val = kwargs.get(self.MP_MINVAL, None)
        self._muta_max_val = kwargs.get(self.MP_MAXVAL, None)
        self._muta_step = kwargs.get(self.MP_STEP, None)
        self._muta_fget = kwargs.get(self.MP_FGET, None)
        self._muta_fset = kwargs.get(self.MP_FSET, None)
        self._muta_fdel = kwargs.get(self.MP_FDEL, None)
        self._muta_change_callback = kwargs.get(self.MP_CHANGE_CALLBACK, None)
        self._muta_select = kwargs.get(self.MP_SELECT, {})
        self._muta_read_only = kwargs.get(self.MP_READ_ONLY, False)
        # logger.debug("Initializing mutaprop %s with selector %s" % (pid, temp_select))

        # # TODO: rewrite to mutasource
        # if isinstance(temp_select, SelectSource):
        #     self._muta_select = temp_select
        # else:
        #     self._muta_select = SelectSource(temp_select)

        self._muta_toggle = kwargs.get(self.MP_TOGGLE, None)

    @property
    def value_type(self):
        return self._muta_value_type

    def _get_kwargs(self):
        temp = {}
        for kwarg in self._allowed_kwargs():
            if kwarg == self.MP_DOC:
                temp[kwarg] = self.__doc__
            else:
                temp[kwarg] = getattr(self, '_muta_{0}'.format(kwarg))

        return temp

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self._muta_fget is None:
            raise MutaPropError("No getter defined.")
        logger.debug("Getting value for %s", self._muta_name)
        return self._muta_fget(obj)

    def __set__(self, obj, value):
        if self._muta_fset is None:
            raise MutaPropError("No setter defined.")

        different = (self._muta_fget(obj) != value)
        self._muta_fset(obj, value)

        # Notify of property change
        try:
            if different and self._muta_change_callback \
             and hasattr(obj, 'muta_id'):
                logger.debug("Notification of set call for %s on %s",
                             self._muta_name, obj.muta_id)
                self._muta_change_callback(obj.muta_id, self._muta_id,
                                           value)
        except AttributeError:
            raise Warning("Property change called on unitialized object.")

    def __delete__(self, obj):
        if self._muta_fdel is None:
            raise MutaPropError("No deleter defined.")
        self._muta_fdel(obj)

    def __str__(self):
        temp = (
            super().__str__() +
            "\nProperty {ro} [{valtyp}] ({minval}, {maxval}, {step}, {select})"
            .format(
                valtyp=self._muta_value_type,
                minval=self._muta_min_val,
                maxval=self._muta_max_val,
                step=self._muta_step,
                select=self._muta_select,
                ro='[Read Only]' if not self.is_writeable() else ''))
        return temp

    def getter(self, fget):
        """ Decorator function for constructing MutaProperty on getter function.
            Takes all ``kwargs`` from :meth:`~mutaprops.MutaProperty.__init__`
        """
        logger.debug("{0}: Getter set".format(self._muta_id))
        temp_kwargs = self._get_kwargs()
        temp_kwargs[self.MP_FGET] = fget
        return type(self)(self._muta_id, self._muta_name, self._muta_value_type,
                          **temp_kwargs)

    def setter(self, func=None, min_val=None, max_val=None, step=None,
               select={}):
        """ Decorator function usable in two ways:
            * decorator without arguments::

                @some_metaprop.setter
                def some_metaprop(self, value):
                    pass


            * decorator with arguments::

                @some_metaprop.setter(min_value=1.0, max_value=2.0)
                def some_metaprop(self, value):
                    pass

        :param func: Is only for internal decorator use, don't use it
        :param min_val: Min. value for numeric types, min. lenght for Strings
        :param max_val: Max. value for numeric types, max. length for Strings
        :param step: Step increment for numeric types
        :param select: Selector object to provide user select. A selector can be
                        either a dict, or list of (label, value) tuples, or
                        another MutaProperty or MutaSource which provides
                        dict or list of tuples. In such case, the selector list
                        will be updated during runtime.

        :returns: MutaProp object
        """
        temp_kwargs = self._get_kwargs()
        temp_kwargs[self.MP_MINVAL] = min_val or self._muta_min_val
        temp_kwargs[self.MP_MAXVAL] = max_val or self._muta_max_val
        temp_kwargs[self.MP_STEP] = step or self._muta_step
        temp_kwargs[self.MP_SELECT] = select or self._muta_select

        if func:
            logger.debug("{0}: Setter set".format(self._muta_id))
            temp_kwargs[self.MP_FSET] = func
            return type(self)(self._muta_id, self._muta_name,
                              self._muta_value_type, **temp_kwargs)

        else:
            def decorator(fset):
                logger.debug("{0}: Setter set".format(self._muta_id))
                temp_kwargs[self.MP_FSET] = fset
                return type(self)(self._muta_id, self._muta_name,
                                  self._muta_value_type, **temp_kwargs)
            return decorator

    def deleter(self, fdel):
        logger.debug("{0}: Deleter set".format(self._muta_id))
        temp_kwargs = self._get_kwargs()
        temp_kwargs[self.MP_FDEL] = fdel
        return type(self)(self._muta_id, self._muta_name, self._muta_value_type,
                          **temp_kwargs)

    def register_change_callback(self, callback):
        self._muta_change_callback = callback

    def to_dict(self, obj=None):

        temp = super().to_dict()

        # Some specific/derived properties follows

        # Override the user setting for read_only if setter is not provided
        if not self.is_writeable():
            temp[self.MP_READ_ONLY] = True

        if obj:
            temp[self.MP_VALUE] = self.__get__(obj)
        temp[self.MP_VALUE_TYPE] = self._muta_value_type.name

        # Remove toggle parameter for non-bool items
        if self._muta_value_type != MutaTypes.BOOL:
            temp.pop(self.MP_TOGGLE)

        return temp

    def muta_set(self, obj, value):
        # TODO: Validation!
        if self._muta_fget(obj) != value:
            logger.debug("Set remotely to %s", str(value))
            self._muta_fset(obj, value)

    def is_writeable(self):
        """ Returns true if only getter is defined.

            Warning: doesn't reflect the read_only kwarg!
        """
        return self._muta_fset is not None


class MutaSource(MutaProperty):
    """ MutaSource is generalized MutaProperty, which is not visible in the
    GUI, however it's changes are reflected in the GUI.
    MutaSource does not need to define display name and value type - any
    serializable type goes.
    MutaSource can also be a class-property.
    MutaSources cannot be directly changed from the GUI layer, however they
    can be changed indirectly from the model/MutaObject itself.

    **Implementation Note**

    In theory :class:`~mutaprops.mutaprops.MutaProperty` should be child of
    :class:`~mutaprops.mutaprops.MutaSource`, in practice the differences are of such
    character it doesn't make it more convenient to implement
    :class:`~mutaprops.mutaprops.MutaSource` as child of :class:`~mutaprops.mutaprops.MutaProperty`.
    """
    MP_CLASS_TYPE = 'source'

    MP_CLASS_SCOPE = 'class_scope'
    MP_OWNER_CLASS = 'owner_class'


    @classmethod
    def _allowed_kwargs(cls):
        return cls.MP_DOC, cls.MP_CLASS_SCOPE, cls.MP_FGET, cls.MP_FSET, \
               cls.MP_FDEL, cls.MP_CHANGE_CALLBACK, cls.MP_OWNER_CLASS

    @classmethod
    def _exported_params(cls):
        return cls.MP_ID, cls.MP_DOC, cls.MP_TYPE, cls.MP_CLASS_SCOPE

    @classmethod
    def serialize(cls, value):
        if isinstance(value, MutaProperty):
            return {cls.MP_TYPE: value.MP_CLASS_TYPE, cls.MP_ID: value._muta_id}
        else:
            return value

    def __init__(self, pid, display_name, value_type, **kwargs):
        """ Init signature is kept for convenience, however
            `display_name` and `value_type` are ignored.

        :param kwargs:  Optional attibutes
            * `fget` :      function
                            Getter function
            * `fset` :      function
                            Setter function
            * `fdel` :      function
                            Deleter function
            * `class_scope` : bool
                            Set to true if the exposed property is a property
                            of a class.
        """

        doc = kwargs.get(self.MP_DOC, None)
        fget = kwargs.get(self.MP_FGET, None)

        if doc is None and fget is not None:
            kwargs[self.MP_DOC] = fget.__doc__

        MutaProp.__init__(self, pid, pid, **kwargs)

        self._muta_fget = kwargs.get(self.MP_FGET, None)
        self._muta_fset = kwargs.get(self.MP_FSET, None)
        self._muta_fdel = kwargs.get(self.MP_FDEL, None)
        self._muta_change_callback = kwargs.get(self.MP_CHANGE_CALLBACK, None)
        self._muta_class_scope = kwargs.get(self.MP_CLASS_SCOPE, False)
        self._muta_owner_class = kwargs.get(self.MP_OWNER_CLASS, None)

        self._muta_value_type = None

    @property
    def class_scoped(self):
        """
        :return: True if the MutaSource is classproperty.
        """
        return self._muta_class_scope

    @property
    def owner_class(self):
        """ In case of classproperty source, returns the owner class."""
        return self._muta_owner_class

    def set_owner_class(self, defining_class):
        self._muta_owner_class = defining_class

    # Overload to disable
    def muta_set(self, obj, value):
        raise MutaPropError("Source cannot be set frou GUI layer.")

    def __str__(self):
        return "MutaSource ID: {pid}, Description: {doc}".format(
            pid=self._muta_id,
            doc=self.__doc__
        )

    def __call__(self, value):
        if self._muta_class_scope:
            self.__set__(None, value)

    def __get__(self, obj, objtype=None):
        if obj is None:
            if self._muta_class_scope:
                obj = objtype
            else:
                raise MutaPropError("Object not specified.")

        if self._muta_fget is None:
            raise MutaPropError("No getter defined.")

        logger.debug("Getting value for %s", self._muta_name)
        return self._muta_fget(obj)

    def setter(self, func):
        """ Get setter method.
        :param func:
        :return: MutaSource object.
        """
        temp_kwargs = self._get_kwargs()

        logger.debug("{0}: Setter set".format(self._muta_id))
        temp_kwargs[self.MP_FSET] = func
        return type(self)(self._muta_id, self._muta_name,
                          self._muta_value_type, **temp_kwargs)

    def setter_classproperty(self, func):

        if not self._muta_class_scope:
            raise MutaPropError("Initializing class property setter" +
                                " for property without class scope.")

        def class_scoped_setter(cls, value):

            different = self._muta_fget(cls) != value
            func(cls, value)

            # Notify of property change
            if different and self._muta_change_callback:
                logger.debug("Notification of set on mutaselect on %s", id(cls))
                self._muta_change_callback(cls._orig_cls.__name__,
                                           self._muta_id,
                                           value)

        return classmethod(class_scoped_setter)

    def to_dict(self, obj=None):
        temp = MutaProp.to_dict(self)
        logger.debug("Serializing mutasource: {0}".format(temp))

        if obj:
            temp[self.MP_VALUE] = self.__get__(obj)

        return temp


class MutaAction(MutaProp):

    MP_CLASS_TYPE = 'action'
    MP_READ_ONLY = 'read_only'  # GUI Read only setting

    @classmethod
    def _allowed_kwargs(cls):
        return super()._allowed_kwargs() + (cls.MP_READ_ONLY,)

    @classmethod
    def _exported_params(cls):
        return super()._exported_params() + (cls.MP_READ_ONLY,)

    def __init__(self, pid, display_name, callback, **kwargs):

        doc = kwargs.get(self.MP_DOC, None)

        if doc is None:
            kwargs[self.MP_DOC] = callback.__doc__

        super().__init__(pid, display_name, **kwargs)

        self._muta_read_only = kwargs.get(self.MP_READ_ONLY, False)

        self._callback = callback

    def muta_call(self, obj):
        if not hasattr(obj, '_muta_obj_id'):
            raise MutaPropError("Executing action on uninitialized MutaObject.")

        logger.debug("%s: External execution call on %s", self._muta_id,
                     obj._muta_obj_id)
        self.__call__(obj)

    def __call__(self, obj):
        if self._callback is None:
            raise MutaPropError("No callback is defined.")
        self._callback(obj)

    # It's necessary to use non-data descriptor to make this callable class
    # capable of binding a method
    # https://docs.python.org/3.5/howto/descriptor.html#functions-and-methods
    # http://stackoverflow.com/questions/972/adding-a-method-to-an-existing-object-instance
    # http://stackoverflow.com/questions/26226604/decorating-a-class-function-with-a-callable-instance
    def __get__(self, obj, objtype=None):
        return types.MethodType(self, obj)


class MutaPropClass(object):

    MP_OBJ_ID = 'obj_id'
    MP_CLASS_ID = 'class_id'
    MP_PROPS = 'props'
    MP_NAME = 'name'
    MP_GUI_ID = 'gui_id'
    MP_GUI_MAJOR_VERSION = 'gui_major_version'
    MP_GUI_MINOR_VERSION = 'gui_minor_version'
    MP_DOC = 'doc'

    @classmethod
    def _exported_params(cls):
        return (cls.MP_OBJ_ID, cls.MP_NAME, cls.MP_PROPS,
                cls.MP_GUI_MAJOR_VERSION, cls.MP_GUI_MINOR_VERSION,
                cls.MP_DOC, cls.MP_CLASS_ID)

    def update_props(self, change_callback=None):
        """Because this is potentially heavy operation and property definitions
        are not likely to be changed during objects lifetime, it's easier to
        cache it.
        """
        temp = []

        for basecls in type(self).mro():
            for prop, value in basecls.__dict__.items():
                if isinstance(value, MutaProp):
                    logger.debug("Adding mutaprop: {0}".format(value.prop_id))
                    temp.append(value)
                if isinstance(value, MutaProperty):
                    value.register_change_callback(change_callback)
                if isinstance(value, MutaSource):
                    if value.class_scoped:
                        value.set_owner_class(self.__class__)

        temp.sort(key=lambda x: x.definition_order)
        setattr(self, self.muta_attr(self.MP_PROPS),
                OrderedDict([(prop.prop_id, prop) for prop in temp]))

    @property
    def props(self):
        return getattr(self, self.muta_attr(self.MP_PROPS))

    @property
    def muta_id(self):
        return getattr(self, self.muta_attr(self.MP_OBJ_ID))

    # Normal properties cannot be used on class variables, so going with get_*
    @classmethod
    def get_class_name(cls):
        return getattr(cls, cls.muta_attr(cls.MP_NAME))

    @classmethod
    def get_gui_version(cls):
        return (getattr(cls, cls.muta_attr(cls.MP_GUI_MAJOR_VERSION)),
                getattr(cls, cls.muta_attr(cls.MP_GUI_MINOR_VERSION)))

    @classmethod
    def get_gui_id(cls):
        return getattr(cls, cls.muta_attr(cls.MP_GUI_ID))

    @classmethod
    def muta_attr(cls, attr):
        return '_muta_{0}'.format(attr)

    def muta_init(self, object_id, change_callback=None):
        self.update_props(change_callback)
        setattr(self, self.muta_attr(self.MP_OBJ_ID), object_id)

    def muta_unregister(self):
        self.update_props(change_callback=None)

    def is_muta_ready(self):
        if (hasattr(self, self.muta_attr(self.MP_OBJ_ID)) and
                (self.muta_id is not None)):
            return True
        else:
            return False

    def to_dict(self):
        temp = {}
        for attr in self._exported_params():
            if attr == self.MP_DOC:
                temp[self.MP_DOC] = rest_to_html(self.__doc__)
            elif attr == self.MP_CLASS_ID:
                temp[self.MP_CLASS_ID] = self._orig_cls.__name__
            else:
                attr_value = getattr(self, self.muta_attr(attr))
                if attr == self.MP_PROPS:
                    attr_value = [prop.to_dict(obj=self) for prop in
                                  attr_value.values()]

                temp[attr] = attr_value

        return temp


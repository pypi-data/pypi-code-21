#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: hoonds.patterns.observer
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Here we have classes and utilities for implementing the
`observer <https://en.wikipedia.org/wiki/Observer_pattern>`_ pattern.
"""

import inspect
from pydispatch import dispatcher
from typing import Callable
from enum import Enum
from abc import ABCMeta
from typing import Any, Dict, List
from collections import Mapping


class SignalsEnum(object):
    """
    This is a flag interface applied to classes decorated with the :py:func:`signals` decorator.
    """
    pass


def signals():
    """
    Use this decorator to identify the enumeration within your observable class that defines the class' signals.
    """
    # We need an inner function that actually adds the logger instance to the class.
    def add_signals(cls):
        # If the class doesn't already extend SignalsEnum...
        if SignalsEnum not in cls.__bases__:
            # ...the decorator tells us that it should.
            cls.__bases__ += (SignalsEnum,)
        return cls
    # Return the inner function.
    return add_signals


class SignalArgs(Mapping):
    """
    This is a read-only dictionary that holds signal arguments as they're transmitted to receivers.

    .. note::

        You can extend this class to provide explicit properties, however you are advised to store the underlying
        values in the dictionary.
    """

    def __init__(self, data: Dict[str, Any]=None):
        """

        :param data: the arguments
        :type data:  :py:class:`Dict[str, Any]`
        """
        self._data = data if data is not None else {}

    def get(self, key) -> Any:
        """
        Get the value of a property by its name.
        :param key: the property name
        :return: the value
        """
        return self._data[key]

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    @property
    def is_empty_set(self) -> bool:
        """
        Is the argument set empty?

        :return: ``True`` if the argument set is empty, otherwise ``False``.
        :rtype:  ``bool``
        """
        # We consider the
        return len(self.keys()) != 0


class SubscriberHandle(object):
    """
    This is a handle object that is returned when you subscribe to a signal.  It can be used to unsubscribe when
    you're no longer interested in receiving the dispatches.
    """
    def __init__(self,
                 signal: Enum,
                 receiver: Callable[[SignalArgs], None],
                 sender: Any):
        self._signal: Enum = signal
        self._receiver: Callable[[SignalArgs]] = receiver
        self._sender: Any = sender

    @property
    def signal(self) -> Enum:
        """
        Get the signal.

        :rtype:  :py:class:`Enum`
        """
        return self._signal

    @property
    def receiver(self) -> Callable[[SignalArgs], None]:
        """
        Get the receiver.

        :rtype:  :py:class:`Callable`
        """
        return self._receiver

    @property
    def sender(self) -> Any:
        """
        Get the sender.

        :rtype:  :py:class:`Any`
        """
        return self._sender

    def unsubscribe(self):
        """
        Unsubscribe from the signal.
        """
        dispatcher.disconnect(receiver=self.receiver, signal=self.signal, sender=self.sender)


class Observable(object):
    """
    Extend this class to implement the observer pattern.
    """
    __metaclass__ = ABCMeta

    # NOTE:  We don't do any work in the constructor.  We do this as a matter of design to remove any obligation on
    # the part of the subclass to class this class' constructor.

    @classmethod
    def _get_signals(cls) -> Enum or None:
        """
        Get the signals enumeration defined for class.
        """
        # If this isn't the first time we've received this request...
        try:
            # ...we should have added the 'signals enumeration' attribute to the class.
            return cls._signals_enum
        except AttributeError:  # Oops!  It looks like this is the first time, but no problem.
            # Let's see if there are any signals defined.
            _signals_enums: List[SignalsEnum] = [
                tup[1] for tup in inspect.getmembers(cls)
                if isinstance(tup[1], type)
                and Enum in tup[1].__bases__
                and SignalsEnum in tup[1].__bases__
            ]
            # How many do we have?
            count = len(_signals_enums)
            # If we don't have any signals enumerations...
            if count == 0:
                cls._signals_enum = None  # ...that's odd, but OK.
            elif count == 1:  # If we have exactly one..
                cls._signals_enum = _signals_enums[0]  # ...that's great.  It's what we expected.
            else:
                # We have a problem.
                raise TypeError('The signals enumeration may only be defined once.')
            # At this point, we definitely have the property, so we're good to go.
            return cls._signals_enum

    @property
    def signals(self) -> Enum or None:
        """
        Get this observable's enumeration of signals.  Subclasses should override the property to return their
        particular enumeration of signals.

        :return: the enumeration that defines the signals
        :rtype:  :py:class:`Enum`
        """
        return self._get_signals()

    def subscribe(self,
                  signal: Enum, receiver: Callable[[SignalArgs], None],
                  weak: bool=True) -> SubscriberHandle:
        """
        Subscribe to a signal.

        :param signal: this is the signal to which you're subscribing
        :type signal:  :py:class:`Enum`
        :param receiver: this is the function or method that will handle the dispatch
        :type receiver:  :py:class:`Callable[[SignalArguments]]`
        :param weak:  When ``True`` the dispatcher maintains a weak reference to the receiver which will not prevent
            garbage collection.
        :type weak:  ``bool``
        :return: a handle that can be used to unsubscribe from the signal
        :rtype:  :py:class:`SubscriberHandle`

        .. note::

            If the receiver is a lambda function, or otherwise might need to receive signals after it goes out of
            scope, you likely want the ``weak`` parameter to be ``True``, however you must remember that any time
            this argument is ``True`` you are responsible for making sure the receiver is unsubscribed to prevent
            memory leaks.
        """
        handle = SubscriberHandle(signal=signal, receiver=receiver, sender=self)
        dispatcher.connect(receiver=handle.receiver, signal=handle.signal, sender=handle.sender, weak=weak)
        return handle

    def send_signal(self, signal: Enum, args: SignalArgs or dict=None):
        """
        Send a signal to any interested parties.

        :param signal: the signal
        :type signal:  :py:class:`Enum`
        :param args: the arguments to the receiver
        :type args:  :py:class:`Any`
        """
        _args = None # Let's figure out what kind of arguments we're dealing with.
        # If we got nothing (fairly likely)...
        if args is None:
            # ...normalize the value.
            _args = SignalArgs({})
        elif isinstance(args, dict):
            # If we got a dict (people are lazy, so this is pretty likely), convert it to a signal argument object.
            _args = SignalArgs(args)
        elif isinstance(args, SignalArgs):
            # If we got an actual signal argument object, that's pretty easy.
            _args = args
        else:  # Oops.  We didn't get *any* of the above.  So we have a problem.
            raise TypeError('Arguments must be {sig_arg_typ} or {dict_typ}'.format(
                sig_arg_typ=SignalArgs.__name__,
                dict_typ=dict.__name__
            ))
        # Now we can dispatch the signal.
        dispatcher.send(signal, self, _args)

    def unsubscribe_all(self):
        """
        Disconnect all the receivers.
        """
        dispatcher.disconnect(dispatcher.Any, self)

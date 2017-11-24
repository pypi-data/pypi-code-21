# -*- coding: utf-8 -*-
"""
Manage bindings for :class:`clik.magic.Magic` variables.

:author: Joe Joyce <joe@decafjoe.com>
:copyright: Copyright (c) Joe Joyce and contributors, 2009-2017.
:license: BSD
"""
import contextlib

from clik.compat import iteritems


class LockedMagicError(Exception):
    """Raised when trying to acquire a magvar that is already acquired."""

    def __init__(self, name):
        """
        Initialize the exception.

        :param str name: Name of the magic variable that is locked.
        """
        msg = 'The magic variable "%s" is currently locked' % name
        super(LockedMagicError, self).__init__(msg)

        #: Name of the magic variable that is locked.
        #:
        #: :type: :class:`str`
        self.name = name


class MagicNameConflictError(Exception):
    """Raised when trying to register an already-registered magvar."""

    def __init__(self, name):
        """
        Initialize the exception.

        :param str name: Name of the magic variable that is already registered.
        """
        msg = 'The magic variable name "%s" is already registered' % name
        super(MagicNameConflictError, self).__init__(msg)

        #: Name of the magic variable that is already registered.
        #:
        #: :type: :class:`str`
        self.name = name


class UnregisteredMagicNameError(Exception):
    """Raised when trying to access an unregistered magic variable."""

    def __init__(self, name):
        """
        Initialize the exception.

        :param str name: Name of the unregistered magic variable the caller
                         was attempting to access.
        """
        msg = 'The magic variable "%s" is not registered' % name
        super(UnregisteredMagicNameError, self).__init__(msg)

        #: Name of the magic variable that is unregistered.
        #:
        #: :type: :class:`str`
        self.name = name


class UnboundMagicError(Exception):
    """Raised when trying to access a magic variable that is not bound."""

    def __init__(self, name):
        """
        Initialize the exception.

        :param str name: Name of the unbound magic variable the caller was
                         attempting to access.
        """
        msg = 'The magic variable "%s" is not bound' % name
        super(UnboundMagicError, self).__init__(msg)

        #: Name of the magic variable that is unbound.
        #:
        #: :type: :class:`str`
        self.name = name


class Context(object):
    """Bindings manager for magic variables."""

    def __init__(self):
        """Initialize the context."""
        self._registry = []
        self._state = {}

    @contextlib.contextmanager
    def __call__(self, **kwargs):
        """
        Context manager for :meth:`push` -ing ``kwargs`` during a code block.

        Example::

           context = Context()
           context.register('foo')
           with context(foo='bar'):
               pass  # do some stuff

        Before the block, each key/value pair in ``kwargs`` is passed to
        :meth:`push`. After the block, each key is :meth:`pop` -ped.
        """
        keys = []
        for key, value in iteritems(kwargs):
            self.push(key, value)
            keys.append(key)
        yield
        for key in keys:
            self.pop(key)

    @contextlib.contextmanager
    def acquire(self, *magic_variables):
        """
        Context manager to lock ``magic_variables`` from use by other contexts.

        Only one context at a time is allowed to control the binding of a magic
        variable. Using this context manager ensures the caller can safely
        manipulate the binding without interference from other contexts::

           foo = Magic('foo')
           context1 = Context()
           context1.register('foo')
           context2 = Context()
           context2.register('foo')
           with context1.acquire(foo):
               with context1(foo='bar'):
                   pass  # do some stuff
               with context2.acquire(foo):
                   # BOOM! LockedMagicError gets thrown

        Before the block, each of the ``magic_variables`` is checked to see if
        it currently has a context. If so, :exc:`LockedMagicError` is thrown.
        Otherwise, the context is set to this instance.

        After the block, the context for each magic variable is reset to
        ``None``, freeing it up for use by other contexts.

        :raise: :exc:`LockedMagicError` if one of ``magic_variables`` is
                already acquired
        """
        for variable in magic_variables:
            if variable._Magic__context is not None:
                raise LockedMagicError(variable._Magic__context)
            self.register(variable._Magic__name)
            object.__setattr__(variable, '_Magic__context', self)
        try:
            yield
        finally:
            for variable in magic_variables:
                self.unregister(variable._Magic__name)
                object.__setattr__(variable, '_Magic__context', None)

    def _assert_in_registry(self, name):
        if name not in self._registry:
            raise UnregisteredMagicNameError(name)

    def get(self, name):
        """
        Return currently-bound value of magic variable named ``name``.

        :param str name: Name of magic variable.
        :raise: :exc:`UnregisteredMagicNameError` if ``name`` is not registered
        :raise: :exc:`UnboundMagicError` if variable is not currently bound
        """
        self._assert_in_registry(name)
        if not self._state[name]:
            raise UnboundMagicError(name)
        return self._state[name][0]

    def push(self, name, obj):
        """
        Push a value on to a variable's stack, rebinding its current value.

        :param str name: Name of magic variable.
        :param obj: New value to push on to the stack.
        :raise: :exc:`UnregisteredMagicNameError` if ``name`` is not registered
        """
        self._assert_in_registry(name)
        self._state[name].insert(0, obj)

    def pop(self, name):
        """
        Pop and return the current value off the variable's stack.

        This rebinds the variable to the next-highest item on the stack.

        :param str name: Name of magic variable.
        :raise: :exc:`UnregisteredMagicNameError` if ``name`` is not registered
        :raise: :exc:`UnboundMagicError` if variable is not currently bound
        """
        self._assert_in_registry(name)
        if not self._state[name]:
            raise UnboundMagicError(name)
        return self._state[name].pop(0)

    def register(self, name):
        """
        Register a magic variable name.

        Requiring registration prevents accidental conflicts between modules.
        If two modules (which may not know about each other) both try to
        register the same magic variable, clik will thrown an exception.

        :param str name: Name of magic variable.
        :raise: :exc:`MagicNameConflictError` if ``name`` is already registered
        """
        if name in self._registry:
            raise MagicNameConflictError(name)
        self._registry.append(name)
        self._state[name] = []

    def unregister(self, name):
        """
        Unregister a magic variable name.

        :param str name: Name of magic variable.
        :raise: :exc:`UnregisteredMagicNameError` if ``name`` is not registered
        """
        self._assert_in_registry(name)
        self._registry.remove(name)
        del self._state[name]

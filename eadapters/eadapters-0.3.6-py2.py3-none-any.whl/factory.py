#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading

import appier

from . import budy_a

class Factory(object):

    ADAPTERS = dict(
        budy = budy_a.BudyAdapter
    )

    INSTANCES = dict()

    LAST_INSTANCE_MAP = dict()

    STORE_INSTANCES = False

    @classmethod
    def get_adapter(cls, name = "local", context = {}, extra = {}):
        # retrieves the unique identifier of the adapter from the
        # provided context and then tries to build the proper instance
        # identifier using it, note that the identifier is not
        # considered valid in case no uuid is defined in context
        context_t = context.get("uuid", None)
        identifier = (name, context_t)
        is_valid = True if context and context_t else False

        # tries to retrieve the adapter, and in case there's a match
        # the context is set in it and the last instance reference is
        # updates so that global operations may use a "new" context
        adapter = cls.INSTANCES.get(identifier, None) if is_valid else None
        if adapter:
            adapter.set_context(context)
            cls._set_instance(adapter)
            return adapter

        # tries to retrieve the adapter class from the map that associates
        # the various adapter class name with the adapters
        adapter_c = cls.ADAPTERS.get(name, None)
        if not adapter_c: raise appier.OperationalError(
            message = "Adapter '%s' not found" % name,
            code = 400
        )

        # duplicates the context map and extends it with the proper extra
        # value, using then the result in the creation of the adapter
        context = dict(context)
        context.update(extra)
        adapter = adapter_c(**context)

        # re-retrieves the context from the created adapters and uses it
        # to re-build the "target" identifier of the adapter
        context = adapter.get_context()
        context_t = context.get("uuid", None)
        identifier = (name, context_t)

        # sets the adapters in the global list of instances and then call
        # the set instance method in the current class
        if cls.STORE_INSTANCES: cls.INSTANCES[identifier] = adapter
        cls._set_instance(adapter)
        return adapter

    @classmethod
    def get_adapter_l(cls):
        if appier.is_safe(): return None
        return cls._get_instance()

    @classmethod
    def _get_instance(cls):
        tid = threading.current_thread().ident
        return cls.LAST_INSTANCE_MAP.get(tid)

    @classmethod
    def _set_instance(cls, adapter):
        tid = threading.current_thread().ident
        cls.LAST_INSTANCE_MAP[tid] = adapter

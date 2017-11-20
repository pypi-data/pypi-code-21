""" AppOptics instrumentation for memcache client module.

Copyright (C) 2016 by SolarWinds, LLC.
All rights reserved.
"""
from appoptics import util
import socket
from functools import partial, wraps

appoptics_logger = util.logger

# memcache.Client methods (from docstring)
# Setup: __init__, set_servers, forget_dead_hosts, disconnect_all, debuglog
# Insertion: set, add, replace, set_multi
# Retrieval: get, get_multi
# Integers: incr, decr
# Removal: delete, delete_multi
# Mutate: append, cas, prepend

# memcache.Client setup
MC_SERVER_COMMANDS = set(('__init__', 'set_servers'))

# these methods also have the same names as Memcached commands/ops
MC_COMMANDS = set(('get', 'get_multi',
                   'set', 'add', 'replace', 'set_multi',
                   'incr', 'decr',
                   'delete', 'delete_multi',
                   'append', 'cas', 'prepend', 'gets'))


def wrap_mc_method(func, f_args, f_kwargs, return_val, funcname=None):
    """Pulls the operation and (for get) whether a key was found, on each public method."""
    kvs = {}
    if funcname in MC_COMMANDS:
        kvs['KVOp'] = funcname
    # could examine f_args for key(s) here
    if funcname == 'get':
        kvs['KVHit'] = int(return_val is not None)
    return kvs


def wrap_get_server(layer_name, func):
    """ Wrapper for memcache._get_server, to read remote host on all ops.

    This relies on the module internals, and just sends an info event when this
    function is called.
    """
    @wraps(func) # XXX Not Python2.4-friendly
    def wrapper(*f_args, **f_kwargs):
        ret = func(*f_args, **f_kwargs)
        try:
            args = {'KVKey': f_args[1]}
            (host, _) = ret
            if host:
                if host.family == socket.AF_INET:
                    args['RemoteHost'] = host.ip
                elif host.family == socket.AF_UNIX:
                    args['RemoteHost'] = 'localhost'

            util.log('info', layer_name, keys=args,
                     store_backtrace=util._collect_backtraces('memcache')
                     )
        except Exception as e:
            appoptics_logger.error("AppOptics error: %s" % str(e))

        return ret
    return wrapper


def dynamic_wrap(fn):
    # We explicity pass assigned to wraps; this skips __module__ from the
    # default list, which doesn't exist for the functions from pylibmc.
    @wraps(fn, assigned=('__name__', '__doc__'))
    def wrapped(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapped


def wrap(layer_name, module):
    try:
        # wrap middleware callables we want to wrap
        cls = getattr(module, 'Client', None)
        if not cls:
            return
        for method in MC_COMMANDS:
            # delete_multi delegates to delete in pylibmc, so don't instrument it
            if method == 'delete_multi' and module.__name__ == 'pylibmc':
                continue
            fn = getattr(cls, method, None)
            if not fn:
                # this method does not exist for this module/version
                continue
            kvs = {'Class': layer_name + '.Client',
                   'Function': method}
            wrapfn = fn if hasattr(fn, '__func__') else dynamic_wrap(fn)
            wrapper = util.log_method(layer_name,
                                      callback=partial(wrap_mc_method, funcname=method),
                                      entry_kvs=kvs)
            setattr(cls, method, wrapper(wrapfn))

        # per-key memcache host hook
        if hasattr(cls, '_get_server'):
            fn = getattr(cls, '_get_server', None)
            setattr(cls, '_get_server', wrap_get_server(layer_name, fn))

    except Exception as e:
        appoptics_logger.error("AppOptics error: %s" % str(e))

if util.ready():
    for module_name in ['memcache', 'pylibmc']:
        try:
            mod = __import__(module_name)
            wrap(module_name, mod)
        except (ImportError, KeyError) as ex:
            pass

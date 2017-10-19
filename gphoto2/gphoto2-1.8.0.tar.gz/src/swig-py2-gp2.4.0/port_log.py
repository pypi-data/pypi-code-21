# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.10
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info as _swig_python_version_info
if _swig_python_version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _port_log.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if _swig_python_version_info >= (2, 7, 0):
    def swig_import_helper():
        import importlib
        pkg = __name__.rpartition('.')[0]
        mname = '.'.join((pkg, '_port_log')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_port_log')
    _port_log = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_port_log', [dirname(__file__)])
        except ImportError:
            import _port_log
            return _port_log
        if fp is not None:
            try:
                _mod = imp.load_module('_port_log', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _port_log = swig_import_helper()
    del swig_import_helper
else:
    import _port_log
del _swig_python_version_info
try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.

try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if (name == "thisown"):
        return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if (not static):
        object.__setattr__(self, name, value)
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr(self, class_type, name):
    if (name == "thisown"):
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    raise AttributeError("'%s' object has no attribute '%s'" % (class_type.__name__, name))


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)


def _swig_setattr_nondynamic_method(set):
    def set_attr(self, name, value):
        if (name == "thisown"):
            return self.this.own(value)
        if hasattr(self, name) or (name == "this"):
            set(self, name, value)
        else:
            raise AttributeError("You cannot add attributes to %s" % self)
    return set_attr


GP_LOG_ERROR = _port_log.GP_LOG_ERROR
GP_LOG_VERBOSE = _port_log.GP_LOG_VERBOSE
GP_LOG_DEBUG = _port_log.GP_LOG_DEBUG
GP_LOG_DATA = _port_log.GP_LOG_DATA

def gp_log_add_func(*args):
    """
    gp_log_add_func(GPLogLevel level, GPLogFunc func, void * data) -> int

    Add a function to get logging information.  

    Parameters
    ----------
    * `level` :  
        the maximum level of logging it will get, up to and including the
        passed value  
    * `func` :  
        a GPLogFunc  
    * `data` :  
        data  

    Adds a log function that will be called for each log message that is
    flagged with a log level that appears in given log level. This function
    returns an id that you can use for removing the log function again
    (using gp_log_remove_func).  

    Returns
    -------
    an id or a gphoto2 error code
    """
    return _port_log.gp_log_add_func(*args)

def gp_log_remove_func(id):
    """
    gp_log_remove_func(int id) -> int

    Remove a logging receiving function.  

    Parameters
    ----------
    * `id` :  
        an id (return value of gp_log_add_func)  

    Removes the log function with given id.  

    Returns
    -------
    a gphoto2 error code
    """
    return _port_log.gp_log_remove_func(id)

def gp_log(level, domain, format):
    """
    gp_log(GPLogLevel level, char const * domain, char const * format)

    Log a debug or error message.  

    Parameters
    ----------
    * `level` :  
        gphoto2 log level  
    * `domain` :  
        the log domain  
    * `format` :  
        a printf style format string  
    * `...` :  
        the variable argumentlist for above format string  

    Logs a message at the given log level. You would normally use this
    function to log general debug output in a printf way.
    """
    return _port_log.gp_log(level, domain, format)

import logging

def _gphoto2_logger_cb(level, domain, msg, data):
    log_func, mapping = data
    if level in mapping:
        log_func(mapping[level], '(%s) %s', domain, msg)
    else:
        log_func(logging.ERROR, '%d (%s) %s', level, domain, msg)

def use_python_logging(mapping={}):
    """Install a callback to receive gphoto2 errors and forward them
    to Python's logging system.

    The mapping parameter is a dictionary mapping any of the four
    gphoto2 logging severity levels to a Python logging level. Note that
    anything below Python DEBUG level will not be forwarded.

    """
    full_mapping = {
        GP_LOG_ERROR   : logging.WARNING,
        GP_LOG_VERBOSE : logging.INFO,
        GP_LOG_DEBUG   : logging.DEBUG,
        GP_LOG_DATA    : logging.DEBUG - 5,
        }
    full_mapping.update(mapping)
    log_func = logging.getLogger('gphoto2').log
    for level in (GP_LOG_DATA, GP_LOG_DEBUG, GP_LOG_VERBOSE, GP_LOG_ERROR):
        if full_mapping[level] >= logging.DEBUG:
            break
    return gp_log_add_func(level, _gphoto2_logger_cb, (log_func, full_mapping))




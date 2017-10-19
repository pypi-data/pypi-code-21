# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.10
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info as _swig_python_version_info
if _swig_python_version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _port_info_list.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if _swig_python_version_info >= (2, 7, 0):
    def swig_import_helper():
        import importlib
        pkg = __name__.rpartition('.')[0]
        mname = '.'.join((pkg, '_port_info_list')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_port_info_list')
    _port_info_list = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_port_info_list', [dirname(__file__)])
        except ImportError:
            import _port_info_list
            return _port_info_list
        if fp is not None:
            try:
                _mod = imp.load_module('_port_info_list', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _port_info_list = swig_import_helper()
    del swig_import_helper
else:
    import _port_info_list
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


class PortInfoList(object):
    """Proxy of C _GPPortInfoList struct."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self):
        """__init__(_GPPortInfoList self) -> PortInfoList"""
        _port_info_list.PortInfoList_swiginit(self, _port_info_list.new_PortInfoList())
    __swig_destroy__ = _port_info_list.delete_PortInfoList

    def __len__(self) -> "int":
        """__len__(PortInfoList self) -> int"""
        return _port_info_list.PortInfoList___len__(self)


    def __getitem__(self, idx: 'int') -> "void":
        """__getitem__(PortInfoList self, int idx)"""
        return _port_info_list.PortInfoList___getitem__(self, idx)


    def append(self, info: '_GPPortInfo') -> "void":
        """
        append(PortInfoList self, _GPPortInfo info)

        Append a portinfo to the port information list.  

        Parameters
        ----------
        * `list` :  
            a #GPPortInfoList  
        * `info` :  
            the info to append  

        Appends an entry to the list. This function is typically called by an
        io-driver during #gp_port_library_list. If you leave info.name blank,
        gp_port_info_list_lookup_path will try to match non-existent paths
        against info.path and - if successfull - will append this entry to the
        list.  

        Returns
        -------
        A gphoto2 error code, or an index into the port list (excluding generic
        entries). which can be used for gp_port_info_list_get_info.

        See also gphoto2.gp_port_info_list_append
        """
        return _port_info_list.PortInfoList_append(self, info)


    def load(self) -> "void":
        """
        load(PortInfoList self)

        Load system ports.  

        Parameters
        ----------
        * `list` :  
            a #GPPortInfoList  

        Searches the system for io-drivers and appends them to the list. You
        would normally call this function once after gp_port_info_list_new and
        then use this list in order to supply gp_port_set_info with parameters
        or to do autodetection.  

        Returns
        -------
        a gphoto2 error code

        See also gphoto2.gp_port_info_list_load
        """
        return _port_info_list.PortInfoList_load(self)


    def count(self) -> "int":
        """
        count(PortInfoList self) -> int

        Number of ports in the list.  

        Parameters
        ----------
        * `list` :  
            a #GPPortInfoList  

        Returns the number of entries in the passed list.  

        Returns
        -------
        The number of entries or a gphoto2 error code

        See also gphoto2.gp_port_info_list_count
        """
        return _port_info_list.PortInfoList_count(self)


    def lookup_path(self, path: 'char const *') -> "int":
        """
        lookup_path(PortInfoList self, char const * path) -> int

        Lookup a specific path in the list.  

        Parameters
        ----------
        * `list` :  
            a #GPPortInfoList  
        * `path` :  
            a path  

        Looks for an entry in the list with the supplied path. If no exact match
        can be found, a regex search will be performed in the hope some driver
        claimed ports like "serial:*".  

        Returns
        -------
        The index of the entry or a gphoto2 error code

        See also gphoto2.gp_port_info_list_lookup_path
        """
        return _port_info_list.PortInfoList_lookup_path(self, path)


    def lookup_name(self, name: 'char const *') -> "int":
        """
        lookup_name(PortInfoList self, char const * name) -> int

        Look up a name in the list.  

        Parameters
        ----------
        * `list` :  
            a #GPPortInfoList  
        * `name` :  
            a name  

        Looks for an entry in the list with the exact given name.  

        Returns
        -------
        The index of the entry or a gphoto2 error code

        See also gphoto2.gp_port_info_list_lookup_name
        """
        return _port_info_list.PortInfoList_lookup_name(self, name)


    def get_info(self, n: 'int const') -> "void":
        """
        get_info(PortInfoList self, int const n)

        Get port information of specific entry.  

        Parameters
        ----------
        * `list` :  
            a #GPPortInfoList  
        * `n` :  
            the index of the entry  
        * `info` :  
            the returned information  

        Returns a pointer to the current port entry.  

        Returns
        -------
        a gphoto2 error code

        See also gphoto2.gp_port_info_list_get_info
        """
        return _port_info_list.PortInfoList_get_info(self, n)

PortInfoList.__len__ = new_instancemethod(_port_info_list.PortInfoList___len__, None, PortInfoList)
PortInfoList.__getitem__ = new_instancemethod(_port_info_list.PortInfoList___getitem__, None, PortInfoList)
PortInfoList.append = new_instancemethod(_port_info_list.PortInfoList_append, None, PortInfoList)
PortInfoList.load = new_instancemethod(_port_info_list.PortInfoList_load, None, PortInfoList)
PortInfoList.count = new_instancemethod(_port_info_list.PortInfoList_count, None, PortInfoList)
PortInfoList.lookup_path = new_instancemethod(_port_info_list.PortInfoList_lookup_path, None, PortInfoList)
PortInfoList.lookup_name = new_instancemethod(_port_info_list.PortInfoList_lookup_name, None, PortInfoList)
PortInfoList.get_info = new_instancemethod(_port_info_list.PortInfoList_get_info, None, PortInfoList)
PortInfoList_swigregister = _port_info_list.PortInfoList_swigregister
PortInfoList_swigregister(PortInfoList)

class _GPPortInfo(object):
    """Proxy of C _GPPortInfo struct."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def get_name(self) -> "void":
        """
        get_name(_GPPortInfo self)

        Get name of a specific port entry.  

        Parameters
        ----------
        * `info` :  
            a #GPPortInfo  
        * `name` :  
            a pointer to a char* which will receive the name  

        Retreives the name of the passed in GPPortInfo, by reference.  

        Returns
        -------
        a gphoto2 error code

        See also gphoto2.gp_port_info_get_name
        """
        return _port_info_list._GPPortInfo_get_name(self)


    def get_path(self) -> "void":
        """
        get_path(_GPPortInfo self)

        Get path of a specific port entry.  

        Parameters
        ----------
        * `info` :  
            a #GPPortInfo  
        * `path` :  
            a pointer to a char* which will receive the path  

        Retreives the path of the passed in GPPortInfo, by reference.  

        Returns
        -------
        a gphoto2 error code

        See also gphoto2.gp_port_info_get_path
        """
        return _port_info_list._GPPortInfo_get_path(self)


    def get_type(self) -> "void":
        """
        get_type(_GPPortInfo self)

        Get type of a specific port entry.  

        Parameters
        ----------
        * `info` :  
            a #GPPortInfo  
        * `type` :  
            a pointer to a GPPortType variable which will receive the type  

        Retreives the type of the passed in GPPortInfo  

        Returns
        -------
        a gphoto2 error code

        See also gphoto2.gp_port_info_get_type
        """
        return _port_info_list._GPPortInfo_get_type(self)

    __swig_destroy__ = _port_info_list.delete__GPPortInfo
_GPPortInfo.get_name = new_instancemethod(_port_info_list._GPPortInfo_get_name, None, _GPPortInfo)
_GPPortInfo.get_path = new_instancemethod(_port_info_list._GPPortInfo_get_path, None, _GPPortInfo)
_GPPortInfo.get_type = new_instancemethod(_port_info_list._GPPortInfo_get_type, None, _GPPortInfo)
_GPPortInfo_swigregister = _port_info_list._GPPortInfo_swigregister
_GPPortInfo_swigregister(_GPPortInfo)

GP_PORT_NONE = _port_info_list.GP_PORT_NONE
GP_PORT_SERIAL = _port_info_list.GP_PORT_SERIAL
GP_PORT_USB = _port_info_list.GP_PORT_USB
GP_PORT_DISK = _port_info_list.GP_PORT_DISK
GP_PORT_PTPIP = _port_info_list.GP_PORT_PTPIP
GP_PORT_USB_DISK_DIRECT = _port_info_list.GP_PORT_USB_DISK_DIRECT
GP_PORT_USB_SCSI = _port_info_list.GP_PORT_USB_SCSI

def gp_port_info_get_name(info: '_GPPortInfo') -> "char **":
    """
    gp_port_info_get_name(_GPPortInfo info) -> int

    Get name of a specific port entry.  

    Parameters
    ----------
    * `info` :  
        a #GPPortInfo  
    * `name` :  
        a pointer to a char* which will receive the name  

    Retreives the name of the passed in GPPortInfo, by reference.  

    Returns
    -------
    a gphoto2 error code

    See also gphoto2.PortInfo.get_name
    """
    return _port_info_list.gp_port_info_get_name(info)

def gp_port_info_get_path(info: '_GPPortInfo') -> "char **":
    """
    gp_port_info_get_path(_GPPortInfo info) -> int

    Get path of a specific port entry.  

    Parameters
    ----------
    * `info` :  
        a #GPPortInfo  
    * `path` :  
        a pointer to a char* which will receive the path  

    Retreives the path of the passed in GPPortInfo, by reference.  

    Returns
    -------
    a gphoto2 error code

    See also gphoto2.PortInfo.get_path
    """
    return _port_info_list.gp_port_info_get_path(info)

def gp_port_info_get_type(info: '_GPPortInfo') -> "GPPortType *":
    """
    gp_port_info_get_type(_GPPortInfo info) -> int

    Get type of a specific port entry.  

    Parameters
    ----------
    * `info` :  
        a #GPPortInfo  
    * `type` :  
        a pointer to a GPPortType variable which will receive the type  

    Retreives the type of the passed in GPPortInfo  

    Returns
    -------
    a gphoto2 error code

    See also gphoto2.PortInfo.get_type
    """
    return _port_info_list.gp_port_info_get_type(info)

def gp_port_info_list_new() -> "GPPortInfoList **":
    """
    gp_port_info_list_new() -> int

    Create a new GPPortInfoList.  

    Parameters
    ----------
    * `list` :  
        pointer to a GPPortInfoList* which is allocated  

    Creates a new list which can later be filled with port infos
    (#GPPortInfo) using gp_port_info_list_load.  

    Returns
    -------
    a gphoto2 error code

    See also gphoto2.PortInfoList.new
    """
    return _port_info_list.gp_port_info_list_new()

def gp_port_info_list_append(list: 'PortInfoList', info: '_GPPortInfo') -> "int":
    """
    gp_port_info_list_append(PortInfoList list, _GPPortInfo info) -> int

    Append a portinfo to the port information list.  

    Parameters
    ----------
    * `list` :  
        a #GPPortInfoList  
    * `info` :  
        the info to append  

    Appends an entry to the list. This function is typically called by an
    io-driver during #gp_port_library_list. If you leave info.name blank,
    gp_port_info_list_lookup_path will try to match non-existent paths
    against info.path and - if successfull - will append this entry to the
    list.  

    Returns
    -------
    A gphoto2 error code, or an index into the port list (excluding generic
    entries). which can be used for gp_port_info_list_get_info.

    See also gphoto2.PortInfoList.append
    """
    return _port_info_list.gp_port_info_list_append(list, info)

def gp_port_info_list_load(list: 'PortInfoList') -> "int":
    """
    gp_port_info_list_load(PortInfoList list) -> int

    Load system ports.  

    Parameters
    ----------
    * `list` :  
        a #GPPortInfoList  

    Searches the system for io-drivers and appends them to the list. You
    would normally call this function once after gp_port_info_list_new and
    then use this list in order to supply gp_port_set_info with parameters
    or to do autodetection.  

    Returns
    -------
    a gphoto2 error code

    See also gphoto2.PortInfoList.load
    """
    return _port_info_list.gp_port_info_list_load(list)

def gp_port_info_list_count(list: 'PortInfoList') -> "int":
    """
    gp_port_info_list_count(PortInfoList list) -> int

    Number of ports in the list.  

    Parameters
    ----------
    * `list` :  
        a #GPPortInfoList  

    Returns the number of entries in the passed list.  

    Returns
    -------
    The number of entries or a gphoto2 error code

    See also gphoto2.PortInfoList.count
    """
    return _port_info_list.gp_port_info_list_count(list)

def gp_port_info_list_lookup_path(list: 'PortInfoList', path: 'char const *') -> "int":
    """
    gp_port_info_list_lookup_path(PortInfoList list, char const * path) -> int

    Lookup a specific path in the list.  

    Parameters
    ----------
    * `list` :  
        a #GPPortInfoList  
    * `path` :  
        a path  

    Looks for an entry in the list with the supplied path. If no exact match
    can be found, a regex search will be performed in the hope some driver
    claimed ports like "serial:*".  

    Returns
    -------
    The index of the entry or a gphoto2 error code

    See also gphoto2.PortInfoList.lookup_path
    """
    return _port_info_list.gp_port_info_list_lookup_path(list, path)

def gp_port_info_list_lookup_name(list: 'PortInfoList', name: 'char const *') -> "int":
    """
    gp_port_info_list_lookup_name(PortInfoList list, char const * name) -> int

    Look up a name in the list.  

    Parameters
    ----------
    * `list` :  
        a #GPPortInfoList  
    * `name` :  
        a name  

    Looks for an entry in the list with the exact given name.  

    Returns
    -------
    The index of the entry or a gphoto2 error code

    See also gphoto2.PortInfoList.lookup_name
    """
    return _port_info_list.gp_port_info_list_lookup_name(list, name)

def gp_port_info_list_get_info(list: 'PortInfoList', n: 'int') -> "GPPortInfo *":
    """
    gp_port_info_list_get_info(PortInfoList list, int n) -> int

    Get port information of specific entry.  

    Parameters
    ----------
    * `list` :  
        a #GPPortInfoList  
    * `n` :  
        the index of the entry  
    * `info` :  
        the returned information  

    Returns a pointer to the current port entry.  

    Returns
    -------
    a gphoto2 error code

    See also gphoto2.PortInfoList.get_info
    """
    return _port_info_list.gp_port_info_list_get_info(list, n)

def gp_port_message_codeset(arg1: 'char const *') -> "char const *":
    """
    gp_port_message_codeset(char const * arg1) -> char const *

    Specify codeset for translations.  

    This function specifies the codeset that are used for the translated
    strings that are passed back by the libgphoto2_port functions.  

    This function is called by the gp_message_codeset() function, there is
    no need to call it yourself.  

    Parameters
    ----------
    * `codeset` :  
        new codeset to use  

    Returns
    -------
    the previous codeset
    """
    return _port_info_list.gp_port_message_codeset(arg1)



# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.10
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info as _swig_python_version_info
if _swig_python_version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _file.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if _swig_python_version_info >= (2, 7, 0):
    def swig_import_helper():
        import importlib
        pkg = __name__.rpartition('.')[0]
        mname = '.'.join((pkg, '_file')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_file')
    _file = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_file', [dirname(__file__)])
        except ImportError:
            import _file
            return _file
        if fp is not None:
            try:
                _mod = imp.load_module('_file', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _file = swig_import_helper()
    del swig_import_helper
else:
    import _file
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



def gp_file_open(filename):
    """
    gp_file_open(char const * filename) -> int

    Parameters
    ----------
    * `file` :  
        a CameraFile  
    * `filename` :  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.open
    """
    return _file.gp_file_open(filename)
class CameraFile(object):
    """The internals of the CameraFile struct are private."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self):
        """
        __init__(_CameraFile self) -> CameraFile

        The internals of the CameraFile struct are private.
        """
        _file.CameraFile_swiginit(self, _file.new_CameraFile())
    __swig_destroy__ = _file.delete_CameraFile

    def set_name(self, name):
        """
        set_name(CameraFile self, char const * name)

        Parameters
        ----------
        * `file` :  
            a CameraFile  
        * `name` :  
            a pointer to a MIME type string  

        Returns
        -------
        a gphoto2 error code.

        See also gphoto2.gp_file_set_name
        """
        return _file.CameraFile_set_name(self, name)


    def get_name(self):
        """
        get_name(CameraFile self)

        Parameters
        ----------
        * `file` :  
            a CameraFile  
        * `name` :  
            a pointer to a name string  

        Returns
        -------
        a gphoto2 error code.

        See also gphoto2.gp_file_get_name
        """
        return _file.CameraFile_get_name(self)


    def set_mime_type(self, mime_type):
        """
        set_mime_type(CameraFile self, char const * mime_type)

        Parameters
        ----------
        * `file` :  
            a CameraFile  
        * `mime_type` :  
            a MIME type string  

        Returns
        -------
        a gphoto2 error code.

        See also gphoto2.gp_file_set_mime_type
        """
        return _file.CameraFile_set_mime_type(self, mime_type)


    def get_mime_type(self):
        """
        get_mime_type(CameraFile self)

        Parameters
        ----------
        * `file` :  
            a CameraFile  
        * `mime_type` :  
            a pointer to a MIME type string  

        Returns
        -------
        a gphoto2 error code.

        See also gphoto2.gp_file_get_mime_type
        """
        return _file.CameraFile_get_mime_type(self)


    def set_mtime(self, mtime):
        """
        set_mtime(CameraFile self, time_t mtime)

        Parameters
        ----------
        * `file` :  
            a CameraFile  
        * `mtime` :  

        Returns
        -------
        a gphoto2 error code.

        See also gphoto2.gp_file_set_mtime
        """
        return _file.CameraFile_set_mtime(self, mtime)


    def get_mtime(self):
        """
        get_mtime(CameraFile self)

        Parameters
        ----------
        * `file` :  
            a CameraFile  
        * `mtime` :  

        Returns
        -------
        a gphoto2 error code.

        See also gphoto2.gp_file_get_mtime
        """
        return _file.CameraFile_get_mtime(self)


    def detect_mime_type(self):
        """
        detect_mime_type(CameraFile self)

        Parameters
        ----------
        * `file` :  
            a CameraFile  

        Returns
        -------
        a gphoto2 error code.

        See also gphoto2.gp_file_detect_mime_type
        """
        return _file.CameraFile_detect_mime_type(self)


    def adjust_name_for_mime_type(self):
        """
        adjust_name_for_mime_type(CameraFile self)

        Parameters
        ----------
        * `file` :  
            a CameraFile  

        Returns
        -------
        a gphoto2 error code.

        See also gphoto2.gp_file_adjust_name_for_mime_type
        """
        return _file.CameraFile_adjust_name_for_mime_type(self)


    def get_name_by_type(self, basename, type):
        """
        get_name_by_type(CameraFile self, char const * basename, CameraFileType type)

        Parameters
        ----------
        * `file` :  
            a CameraFile  
        * `basename` :  
            the basename of the file  
        * `type` :  
            the gphoto type of the file  
        * `newname` :  
            the new name generated  

        Returns
        -------
        a gphoto2 error code.  

        This function takes the basename and generates a filename out of it
        depending on the gphoto filetype and the mime type in the file. The
        gphoto filetype will be converted to a prefix, like thumb_ or raw_, the
        mimetype will replace the current suffix by a different one (if
        necessary).  

        This can be used so that saving thumbnails or metadata will not
        overwrite the normal files.

        See also gphoto2.gp_file_get_name_by_type
        """
        return _file.CameraFile_get_name_by_type(self, basename, type)


    def set_data_and_size(self, data, size):
        """
        set_data_and_size(CameraFile self, char * data, unsigned long size)

        Parameters
        ----------
        * `file` :  
            a CameraFile  
        * `data` :  
        * `size` :  

        Returns
        -------
        a gphoto2 error code.

        See also gphoto2.gp_file_set_data_and_size
        """
        return _file.CameraFile_set_data_and_size(self, data, size)


    def get_data_and_size(self):
        """
        get_data_and_size(CameraFile self)

        Get a pointer to the data and the file's size.  

        Parameters
        ----------
        * `file` :  
            a CameraFile  
        * `data` :  
        * `size` :  

        Returns
        -------
        a gphoto2 error code.  

        Both data and size can be NULL and will then be ignored.  

        The pointer to data that is returned is still owned by libgphoto2 and
        its lifetime is the same as the #file.

        See also gphoto2.gp_file_get_data_and_size
        """
        return _file.CameraFile_get_data_and_size(self)


    def save(self, filename):
        """
        save(CameraFile self, char const * filename)

        Parameters
        ----------
        * `file` :  
            a CameraFile  
        * `filename` :  

        Returns
        -------
        a gphoto2 error code.

        See also gphoto2.gp_file_save
        """
        return _file.CameraFile_save(self, filename)


    def clean(self):
        """
        clean(CameraFile self)

        Parameters
        ----------
        * `file` :  
            a CameraFile  

        Returns
        -------
        a gphoto2 error code.

        See also gphoto2.gp_file_clean
        """
        return _file.CameraFile_clean(self)


    def copy(self, source):
        """
        copy(CameraFile self, CameraFile source)

        Parameters
        ----------
        * `destination` :  
            a CameraFile  
        * `source` :  
            a CameraFile  

        Returns
        -------
        a gphoto2 error code.

        See also gphoto2.gp_file_copy
        """
        return _file.CameraFile_copy(self, source)


    def append(self, data, size):
        """
        append(CameraFile self, char const * data, unsigned long size)

        Parameters
        ----------
        * `file` :  
            a CameraFile  
        * `data` :  
        * `size` :  

        Returns
        -------
        a gphoto2 error code.

        See also gphoto2.gp_file_append
        """
        return _file.CameraFile_append(self, data, size)

CameraFile.set_name = new_instancemethod(_file.CameraFile_set_name, None, CameraFile)
CameraFile.get_name = new_instancemethod(_file.CameraFile_get_name, None, CameraFile)
CameraFile.set_mime_type = new_instancemethod(_file.CameraFile_set_mime_type, None, CameraFile)
CameraFile.get_mime_type = new_instancemethod(_file.CameraFile_get_mime_type, None, CameraFile)
CameraFile.set_mtime = new_instancemethod(_file.CameraFile_set_mtime, None, CameraFile)
CameraFile.get_mtime = new_instancemethod(_file.CameraFile_get_mtime, None, CameraFile)
CameraFile.detect_mime_type = new_instancemethod(_file.CameraFile_detect_mime_type, None, CameraFile)
CameraFile.adjust_name_for_mime_type = new_instancemethod(_file.CameraFile_adjust_name_for_mime_type, None, CameraFile)
CameraFile.get_name_by_type = new_instancemethod(_file.CameraFile_get_name_by_type, None, CameraFile)
CameraFile.set_data_and_size = new_instancemethod(_file.CameraFile_set_data_and_size, None, CameraFile)
CameraFile.get_data_and_size = new_instancemethod(_file.CameraFile_get_data_and_size, None, CameraFile)
CameraFile.save = new_instancemethod(_file.CameraFile_save, None, CameraFile)
CameraFile.clean = new_instancemethod(_file.CameraFile_clean, None, CameraFile)
CameraFile.copy = new_instancemethod(_file.CameraFile_copy, None, CameraFile)
CameraFile.append = new_instancemethod(_file.CameraFile_append, None, CameraFile)
CameraFile_swigregister = _file.CameraFile_swigregister
CameraFile_swigregister(CameraFile)

GP_MIME_TXT = _file.GP_MIME_TXT
GP_MIME_WAV = _file.GP_MIME_WAV
GP_MIME_RAW = _file.GP_MIME_RAW
GP_MIME_PNG = _file.GP_MIME_PNG
GP_MIME_PGM = _file.GP_MIME_PGM
GP_MIME_PPM = _file.GP_MIME_PPM
GP_MIME_PNM = _file.GP_MIME_PNM
GP_MIME_JPEG = _file.GP_MIME_JPEG
GP_MIME_TIFF = _file.GP_MIME_TIFF
GP_MIME_BMP = _file.GP_MIME_BMP
GP_MIME_QUICKTIME = _file.GP_MIME_QUICKTIME
GP_MIME_AVI = _file.GP_MIME_AVI
GP_MIME_CRW = _file.GP_MIME_CRW
GP_MIME_CR2 = _file.GP_MIME_CR2
GP_MIME_NEF = _file.GP_MIME_NEF
GP_MIME_UNKNOWN = _file.GP_MIME_UNKNOWN
GP_MIME_EXIF = _file.GP_MIME_EXIF
GP_MIME_MP3 = _file.GP_MIME_MP3
GP_MIME_OGG = _file.GP_MIME_OGG
GP_MIME_WMA = _file.GP_MIME_WMA
GP_MIME_ASF = _file.GP_MIME_ASF
GP_MIME_MPEG = _file.GP_MIME_MPEG
GP_MIME_AVCHD = _file.GP_MIME_AVCHD
GP_MIME_RW2 = _file.GP_MIME_RW2
GP_MIME_ARW = _file.GP_MIME_ARW
GP_FILE_TYPE_PREVIEW = _file.GP_FILE_TYPE_PREVIEW
GP_FILE_TYPE_NORMAL = _file.GP_FILE_TYPE_NORMAL
GP_FILE_TYPE_RAW = _file.GP_FILE_TYPE_RAW
GP_FILE_TYPE_AUDIO = _file.GP_FILE_TYPE_AUDIO
GP_FILE_TYPE_EXIF = _file.GP_FILE_TYPE_EXIF
GP_FILE_TYPE_METADATA = _file.GP_FILE_TYPE_METADATA
GP_FILE_ACCESSTYPE_MEMORY = _file.GP_FILE_ACCESSTYPE_MEMORY
GP_FILE_ACCESSTYPE_FD = _file.GP_FILE_ACCESSTYPE_FD
GP_FILE_ACCESSTYPE_HANDLER = _file.GP_FILE_ACCESSTYPE_HANDLER

def gp_file_new():
    """
    gp_file_new() -> int

    Create new CameraFile object.  

    Parameters
    ----------
    * `file` :  
        a pointer to a CameraFile  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.new
    """
    return _file.gp_file_new()

def gp_file_new_from_fd(fd):
    """
    gp_file_new_from_fd(int fd) -> int

    Create new CameraFile object from a UNIX filedescriptor.  

    This function takes ownership of the filedescriptor and will close it
    when closing the CameraFile.  

    Parameters
    ----------
    * `file` :  
        a pointer to a CameraFile  
    * `fd` :  
        a UNIX filedescriptor  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.new_from_fd
    """
    return _file.gp_file_new_from_fd(fd)

def gp_file_new_from_handler(handler, priv):
    """
    gp_file_new_from_handler(CameraFileHandler * handler, void * priv) -> int

    Create new CameraFile object using a programmatic handler.  

    Parameters
    ----------
    * `file` :  
        a pointer to a CameraFile  
    * `handler` :  
        a #CameraFileHandler  
    * `private` :  
        a private pointer for frontend use  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.new_from_handler
    """
    return _file.gp_file_new_from_handler(handler, priv)

def gp_file_set_name(file, name):
    """
    gp_file_set_name(CameraFile file, char const * name) -> int

    Parameters
    ----------
    * `file` :  
        a CameraFile  
    * `name` :  
        a pointer to a MIME type string  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.set_name
    """
    return _file.gp_file_set_name(file, name)

def gp_file_get_name(file):
    """
    gp_file_get_name(CameraFile file) -> int

    Parameters
    ----------
    * `file` :  
        a CameraFile  
    * `name` :  
        a pointer to a name string  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.get_name
    """
    return _file.gp_file_get_name(file)

def gp_file_set_mime_type(file, mime_type):
    """
    gp_file_set_mime_type(CameraFile file, char const * mime_type) -> int

    Parameters
    ----------
    * `file` :  
        a CameraFile  
    * `mime_type` :  
        a MIME type string  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.set_mime_type
    """
    return _file.gp_file_set_mime_type(file, mime_type)

def gp_file_get_mime_type(file):
    """
    gp_file_get_mime_type(CameraFile file) -> int

    Parameters
    ----------
    * `file` :  
        a CameraFile  
    * `mime_type` :  
        a pointer to a MIME type string  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.get_mime_type
    """
    return _file.gp_file_get_mime_type(file)

def gp_file_set_mtime(file, mtime):
    """
    gp_file_set_mtime(CameraFile file, time_t mtime) -> int

    Parameters
    ----------
    * `file` :  
        a CameraFile  
    * `mtime` :  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.set_mtime
    """
    return _file.gp_file_set_mtime(file, mtime)

def gp_file_get_mtime(file):
    """
    gp_file_get_mtime(CameraFile file) -> int

    Parameters
    ----------
    * `file` :  
        a CameraFile  
    * `mtime` :  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.get_mtime
    """
    return _file.gp_file_get_mtime(file)

def gp_file_detect_mime_type(file):
    """
    gp_file_detect_mime_type(CameraFile file) -> int

    Parameters
    ----------
    * `file` :  
        a CameraFile  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.detect_mime_type
    """
    return _file.gp_file_detect_mime_type(file)

def gp_file_adjust_name_for_mime_type(file):
    """
    gp_file_adjust_name_for_mime_type(CameraFile file) -> int

    Parameters
    ----------
    * `file` :  
        a CameraFile  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.adjust_name_for_mime_type
    """
    return _file.gp_file_adjust_name_for_mime_type(file)

def gp_file_get_name_by_type(file, basename, type):
    """
    gp_file_get_name_by_type(CameraFile file, char const * basename, CameraFileType type) -> int

    Parameters
    ----------
    * `file` :  
        a CameraFile  
    * `basename` :  
        the basename of the file  
    * `type` :  
        the gphoto type of the file  
    * `newname` :  
        the new name generated  

    Returns
    -------
    a gphoto2 error code.  

    This function takes the basename and generates a filename out of it
    depending on the gphoto filetype and the mime type in the file. The
    gphoto filetype will be converted to a prefix, like thumb_ or raw_, the
    mimetype will replace the current suffix by a different one (if
    necessary).  

    This can be used so that saving thumbnails or metadata will not
    overwrite the normal files.

    See also gphoto2.CameraFile.get_name_by_type
    """
    return _file.gp_file_get_name_by_type(file, basename, type)

def gp_file_set_data_and_size(arg1, data, size):
    """
    gp_file_set_data_and_size(CameraFile arg1, char * data, unsigned long size) -> int

    Parameters
    ----------
    * `file` :  
        a CameraFile  
    * `data` :  
    * `size` :  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.set_data_and_size
    """
    return _file.gp_file_set_data_and_size(arg1, data, size)

def gp_file_get_data_and_size(arg1):
    """
    gp_file_get_data_and_size(CameraFile arg1) -> int

    Get a pointer to the data and the file's size.  

    Parameters
    ----------
    * `file` :  
        a CameraFile  
    * `data` :  
    * `size` :  

    Returns
    -------
    a gphoto2 error code.  

    Both data and size can be NULL and will then be ignored.  

    The pointer to data that is returned is still owned by libgphoto2 and
    its lifetime is the same as the #file.

    See also gphoto2.CameraFile.get_data_and_size
    """
    return _file.gp_file_get_data_and_size(arg1)

def gp_file_save(file, filename):
    """
    gp_file_save(CameraFile file, char const * filename) -> int

    Parameters
    ----------
    * `file` :  
        a CameraFile  
    * `filename` :  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.save
    """
    return _file.gp_file_save(file, filename)

def gp_file_clean(file):
    """
    gp_file_clean(CameraFile file) -> int

    Parameters
    ----------
    * `file` :  
        a CameraFile  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.clean
    """
    return _file.gp_file_clean(file)

def gp_file_copy(destination, source):
    """
    gp_file_copy(CameraFile destination, CameraFile source) -> int

    Parameters
    ----------
    * `destination` :  
        a CameraFile  
    * `source` :  
        a CameraFile  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.copy
    """
    return _file.gp_file_copy(destination, source)

def gp_file_append(arg1, data, size):
    """
    gp_file_append(CameraFile arg1, char const * data, unsigned long size) -> int

    Parameters
    ----------
    * `file` :  
        a CameraFile  
    * `data` :  
    * `size` :  

    Returns
    -------
    a gphoto2 error code.

    See also gphoto2.CameraFile.append
    """
    return _file.gp_file_append(arg1, data, size)



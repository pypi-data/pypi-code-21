import os
import abc

class BaseHoretuException(Exception, metaclass=abc.ABCMeta):
    ok = True
    def __init__(self, message=None, section=tuple(), param=None):
        # message first so it is easy not to provide a section
        if section:
            self.section = section
        else:
            self.section = tuple()
        self.message = message
        self.param = param

    def __repr__(self):
        return '%s(%r, section=%r, param=%r)' % (
            self.__class__.__name__,
            self.message,
            self.section,
            self.param,
        )
    __str__ = __repr__

class ShowHelp(BaseHoretuException):
    pass

class Config(BaseHoretuException):
    def __init__(self, filename):
        self.filename = os.path.expanduser(filename)

class Exit(BaseHoretuException):
    pass

class BaseHoretuError(BaseHoretuException, metaclass=abc.ABCMeta):
    ok = False

class AnnotationNotImplemented(BaseHoretuException):
    pass

class CouldNotParse(BaseHoretuError):
    pass

class Error(BaseHoretuError):
    pass

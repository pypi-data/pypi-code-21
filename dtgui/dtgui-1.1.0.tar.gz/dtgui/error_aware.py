# -*- coding: utf-8 -*-

import traceback
import warnings
from contextlib import suppress
from functools import wraps
from types import FunctionType

from pyqtgraph import QtCore

def error_aware(func):
    """
    Wrap an instance method with a try/except and emit a message.
    Instance that have a signal called 'error_message_signal[str]' will emit
    the exception message upon error via this signal. 
    """
    @wraps(func)
    def aware_func(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except:
            exc = traceback.format_exc()
            with suppress(AttributeError):
                self.error_message_signal.emit(exc)
            warnings.warn(exc, UserWarning)
    return aware_func

class ErrorAware(QtCore.pyqtWrapperType):
    """ 
    Metaclass for QObjects (including QWidgets)
    such that a GUI program will not crash on exception 

    Exception messages are emitted via the object's 'error_message_signal[str]' if
    it is available.
    """
    
    def __new__(meta, classname, bases, class_dict):
        new_class_dict = dict()
        for attr_name, attr in class_dict.items():
            if isinstance(attr, FunctionType):
                attr = error_aware(attr)
            new_class_dict[attr_name] = attr
        
        return super().__new__(meta, classname, bases, new_class_dict)

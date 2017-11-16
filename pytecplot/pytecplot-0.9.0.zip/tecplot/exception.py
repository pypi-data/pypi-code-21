"""
The class hierarchy for |PyTecplot| exceptions are as follows. Exceptions in
parentheses are Python built-ins from which the |PyTecplot| exceptions
derive. One can use either the Python native errors or the more specific
"Tecplot" errors to catch exceptions:

.. code-block:: none

    TecplotError (Exception)
     +--- TecplotConnectionError
     |     `--- TecplotTimeoutError
     +--- TecplotInitializationError (ImportError)
     |     +--- TecplotLicenseError
     |     +--- TecplotLibraryNotLoadedError
     |     `--- TecplotLibraryNotFoundError
     +--- TecplotLogicError (AssertionError)
     +--- TecplotLookupError (LookupError)
     |     +--- TecplotIndexError (IndexError)
     |     `--- TecplotKeyError (KeyError)
     |           `--- TecplotPatternMatchError
     +--- TecplotOSError (OSError)
     +--- TecplotRuntimeError (RuntimeError)
     |     `--- TecplotNotImplementedError (NotImplementedError)
     |           `--- TecplotOutOfDateEngineError
     +--- TecplotSystemError (SystemError)
     |     +--- TecplotMacroError
     +--- TecplotTypeError (TypeError)
     `--- TecplotValueError (ValueError)
"""

from builtins import super

from textwrap import dedent


class TecplotError(Exception):
    """Tecplot error."""


class TecplotConnectionError(TecplotError):
    """Unable to communcate with TecUtil Server."""


class TecplotTimeoutError(TecplotConnectionError):
    """TecUtil Server not responding in a timely fashion."""


class TecplotAttributeError(AttributeError):
    """Undefined attribute."""


class TecplotInitializationError(TecplotError, ImportError):
    """Tecplot engine could not be initialized."""


class TecplotLibraryNotFoundError(TecplotInitializationError):
    """Batch library was not found in PATH or DY/LD_LIBRARY_PATH."""


class TecplotLibraryNotLoadedError(TecplotInitializationError):
    """Batch library could not be loaded."""


class TecplotLicenseError(TecplotInitializationError):
    """Invalid or missing Tecplot license."""


class TecplotLogicError(TecplotError, AssertionError):
    """TecUtil method contract was violated."""


class TecplotLookupError(TecplotError, LookupError):
    """Could not find requested object."""


class TecplotIndexError(TecplotLookupError, IndexError):
    """Index out of range or invalid."""


class TecplotKeyError(TecplotLookupError, KeyError):
    """Key not found."""


class TecplotPatternMatchError(TecplotKeyError):
    """Pattern not found in list of names."""
    def __init__(self, pattern, msg, mode='glob'):
        if mode == 'glob':
            if any(x in pattern for x in ['*', '?', '[', ']']):
                msg += 'For a literal match, the meta-characters: * ? [ ]'
                msg += ' must be wrapped in square-brackets. For example,'
                msg += ' "[?]" matches the character "?".'
        super().__init__(msg)

class TecplotOSError(TecplotError, OSError):
    """Operating system error."""


class TecplotOverflowError(TecplotError, OverflowError):
    """Integer value out of required range."""


class TecplotRuntimeError(TecplotError, RuntimeError):
    """PyTecplot post-initialization error."""


class TecplotNotImplementedError(TecplotRuntimeError, NotImplementedError):
    """Requested operation is planned but not implemented."""


class TecplotOutOfDateEngineError(TecplotNotImplementedError):
    """Requested action is implemented in a newer version of the engine."""
    def __init__(self, sdk_version_supported, message=None):
        """
        Parameters:
            sdk_version (`tuple` of `integers <int>`): The earliest SDK version
                that supports the requested action.
            message (`string <str>`): Message to append to the exception.
        """
        from tecplot import version

        n = len(sdk_version_supported)
        if n < 3:
            sdk_version_supported = tuple(list(sdk_version_supported) +
                                          [0] * (3 - n))

        msg = dedent('''
            The requested action requires an update to
            your installation of Tecplot 360.
                Current Tecplot 360 version: {current}
                Minimum version required: {required}
        '''.format(
            current='{}.{}-{}'.format(*version.sdk_version_info),
            required='{}.{}-{}'.format(*sdk_version_supported)))
        if message:
            msg += '\n' + message
        super().__init__(msg)


class TecplotSystemError(TecplotError, SystemError):
    """Tecplot Engine error or failure."""
    def __init__(self, message=None):
        from tecplot.tecutil import _tecutil_connector
        msgs = []
        if _tecutil_connector.connected and _tecutil_connector.last_message:
            msgs.append(_tecutil_connector.last_message.message)
        if message:
            msgs.append(message)
        super().__init__('\n'.join(str(m) for m in msgs))


class TecplotMacroError(TecplotSystemError):
    """Macro command failed to execute."""


class TecplotTypeError(TecplotError, TypeError):
    """Incorrect or invalid type was used."""


class TecplotValueError(TecplotError, ValueError):
    """Bad value."""


class MESSAGES:
    PERFORMANCE_IMPROVEMENTS = '''\
The performance of this PyTecplot method has been significantly improved in
later versions of Tecplot 360. Please update your installation of Tecplot 360
to the newest version for faster and more reliable script execution.
'''

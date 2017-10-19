# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains all Fastr-related Exceptions
"""

import inspect
import os
import textwrap

# pylint: disable=too-many-ancestors
# Because fo inheriting from FastrError and a common exception causes this
# exception, even though this behaviour is desired


class FastrError(Exception):
    """
    This is the base class for all fastr related exceptions. Catching this
    class of exceptions should ensure a proper execution of fastr.
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor for all exceptions. Saves the caller object fullid (if
        found) and the file, function and line number where the object was
        created.
        """
        super(FastrError, self).__init__(*args, **kwargs)

        frame = inspect.stack()[1][0]
        call_object = frame.f_locals.get('self', None)
        if call_object is not None and hasattr(call_object, 'fullid'):
            self.fastr_object = call_object.fullid
        else:
            self.fastr_object = None

        info = inspect.getframeinfo(frame)
        self.filename = info.filename
        self.function = info.function
        self.linenumber = info.lineno

    def __str__(self):
        """
        String representation of the error

        :return: error string
        :rtype: str
        """
        if self.fastr_object is not None:
            return '[{}] {}'.format(self.fastr_object, super(FastrError, self).__str__())
        else:
            return super(FastrError, self).__str__()

    def excerpt(self):
        """
        Return a excerpt of the Error as a tuple.
        """
        return type(self).__name__, self.message, self.filename, self.linenumber


class FastrNotImplementedError(FastrError, NotImplementedError):
    """
    This function/method has not been implemented on purpose (e.g. should be
    overwritten in a sub-class)
    """
    pass


class FastrOptionalModuleNotAvailableError(FastrNotImplementedError):
    """
    A optional modules for Fastr is needed for this function, but is not
    available on the current python installation.
    """
    pass


class FastrValueError(FastrError, ValueError):
    """
    ValueError in the fastr system
    """
    pass


class FastrCannotChangeAttributeError(FastrError):
    """
    Attempting to change an attribute of an object that can be set only once.
    """


class FastrTypeError(FastrError, TypeError):
    """
    TypeError in the fastr system
    """
    pass


class FastrKeyError(FastrError, KeyError):
    """
    KeyError in the fastr system
    """
    pass


class FastrIndexError(FastrError, IndexError):
    """
    IndexError in the fastr system
    """
    pass


class FastrIndexNonexistent(FastrIndexError):
    """
    This is an IndexError for samples requested from a sparse data array. The
    sample is not there but is probably not there because of sparseness rather
    than being a missing sample (e.g. out of bounds).
    """
    pass


class FastrAttributeError(FastrError, AttributeError):
    """
    AttributeError in the fastr system
    """
    pass


class FastrIOError(FastrError, IOError):
    """
    IOError in the fastr system
    """
    pass


class FastrOSError(FastrError, OSError):
    """
    OSError in the fastr system
    """
    pass


class FastrImportError(FastrError, ImportError):
    """
    ImportError in the fastr system
    """
    pass


class FastrStateError(FastrError):
    """
    An object is in an invalid/unexpected state.
    """
    pass


class FastrSizeUnknownError(FastrError):
    """
    The size of object is not (yet) known and only a theoretical estimate is
    available at the moment.
    """
    pass


class FastrSizeMismatchError(FastrError):
    """
    The size of two object in fastr is not matching where it should.
    """
    pass


class FastrSizeInvalidError(FastrError):
    """
    The given size cannot be valid.
    """
    pass


class FastrCardinalityError(FastrError):
    """
    The description of the cardinality is not valid.
    """
    pass


class FastrUnknownURLSchemeError(FastrKeyError):
    """
    Fastr encountered a data URL with a scheme that was not recognised
    by the IOPlugin manager.
    """
    pass


class FastrDataTypeFileNotReadable(FastrError):
    """
    Could not read the datatype file.
    """
    pass


class FastrDataTypeNotAvailableError(FastrError):
    """
    The DataType requested is not found by the fastr system. Typically this
    means that no matching DataType is found in the DataTypeManager.
    """
    pass


class FastrDataTypeNotInstantiableError(FastrError):
    """
    The base classes for DataTypes cannot be instantiated and should always
    be sub-classed.
    """
    pass


class FastrDataTypeMismatchError(FastrError):
    """
    When using a DataType as the key for the DataTypeManager, the
    DataTypeManager found another DataType with the same name already
    in the DataTypeManager. The means fastr has two version of the same
    DataType in the system, which should never happen!
    """
    pass


class FastrDataTypeValueError(FastrError):
    """
    This value in fastr did not pass the validation specificied for its
    DataType, typically means that the data is missing or corrupt.
    """
    pass


class FastrToolNotAvailableError(FastrError):
    """
    The tool used is not available on the current platform (OS and architecture
     combination) and cannot be used.
    """
    pass


class FastrToolTargetNotFound(FastrError):
    """
    Could not determine the location of the tools target binary/script. The
    tool cannot be used.
    """
    pass


class FastrObjectUnknownError(FastrKeyError):
    """
    Reference to a Tool that is not recognised by the fastr system. This
    typically means the specific id/version combination of the requested
    tool has not been loaded by the ToolManager.
    """
    pass


class FastrNetworkUnknownError(FastrKeyError):
    """
    Reference to a Tool that is not recognised by the fastr system. This
    typically means the specific id/version combination of the requested
    tool has not been loaded by the ToolManager.
    """
    pass


class FastrToolUnknownError(FastrKeyError):
    """
    Reference to a Tool that is not recognised by the fastr system. This
    typically means the specific id/version combination of the requested
    tool has not been loaded by the ToolManager.
    """
    pass


class FastrPluginNotAvailable(FastrKeyError):
    """
    Indicates that a requested Plugin was not found on the system.
    """
    pass

class FastrPluginNotLoaded(FastrStateError):
    """
    The plugin was not successfully loaded. This means the plugin class cannot
    be instantiated.
    """
    pass


class FastrNodeNotValidError(FastrStateError):
    """
    A NodeRun is not in a valid state where it should be, typically an invalid
    NodeRun is passed to the executor causing trouble.
    """
    pass


class FastrNodeNotPreparedError(FastrStateError):
    """
    When trying to access executation data of a NodeRun, the NodeRun must be prepare.
    The NodeRun has not been prepared by the execution, so the data is not
    available!
    """
    pass


class FastrNodeAreadyPreparedError(FastrStateError):
    """
    A attempt is made at preparing a NodeRun for the second time. This is not
    allowed as it would wipe the current execution data and cause data-loss.
    """
    pass


class FastrLookupError(FastrError):
    """
    Could not find specified object in the fastr environment.
    """
    pass


class FastrNetworkMismatchError(FastrError):
    """
    Two interacting objects belong to different fastr network.
    """
    pass


class FastrParentMismatchError(FastrError):
    """
    Two interactive objects have different parent where they should be the same
    """
    pass


class FastrSerializationMethodError(FastrKeyError):
    """
    The desired serialization method does not exist.
    """
    pass


class FastrSerializationError(FastrError):
    """
    The serialization encountered a serious problem
    """

    def __init__(self, message, serializer, original_exception=None):
        # Call superclass
        super(FastrSerializationError, self).__init__(message)

        self.data_path = serializer.data_path
        self.schema_path = serializer.schema_path
        self.object_type = serializer.current_type
        self.current_object = serializer.current_object
        self.current_schema = serializer.current_schema
        if original_exception is not None:
            self.original_exception = original_exception
        else:
            self.original_exception = ''

    def __repr__(self):
        """
        Simple string representation of the exception
        """
        return '<{}: {}>'.format(self.__class__.__name__, self.message)

    def __str__(self):
        """
        Advanced string representation of the exception including the data
        about where in the schema things went wrong.
        """
        return self.message + textwrap.dedent('''

            DATA PATH: {}
            SCHEMA PATH: {}
            CURRENT OBJECT TYPE: {}
            CURRENT OBJECT: {}
            CURRENT SCHEMA: {}

            {}
            '''.rstrip()).format(self.data_path,
                                 self.schema_path,
                                 self.object_type,
                                 self.current_object,
                                 self.current_schema,
                                 self.original_exception)


class FastrSerializationIgnoreDefaultError(FastrSerializationError):
    """
    The value and default are both None, so the value should not be serialized.
    """
    pass


class FastrSerializationInvalidDataError(FastrSerializationError):
    """
    Encountered data to serialize that is invalid given the serialization
    schema.
    """
    pass


class FastrVersionInvalidError(FastrValueError):
    """
    The string representation of the version is malformatted.
    """
    pass


class FastrVersionMismatchError(FastrValueError):
    """
    There is a mismatch between different parts of the Fastr environment
    and integrity is compromised.
    """
    pass


class FastrMountUnknownError(FastrKeyError):
    """
    Trying to access an undefined mount
    """
    pass


class FastrSourceDataUnavailableError(FastrKeyError):
    """
    Could not find the Source data for the desire source.
    """
    pass


class FastrSinkDataUnavailableError(FastrKeyError):
    """
    Could not find the Sink data for the desire sink.
    """
    pass


class FastrExecutionError(FastrError):
    """
    Base class for all fastr execution related errors
    """
    pass


class FastrExecutableNotFoundError(FastrExecutionError):
    """
    The executable could not be found!
    """
    def __init__(self, executable=None, *args, **kwargs):
        super(FastrExecutableNotFoundError, self).__init__(*args, **kwargs)
        self.executable = executable
        self.path = os.environ.get('PATH', '').split(os.pathsep)

    def __str__(self):
        """String representation of the error"""
        return 'Could not find executable "{}" on PATH: {}'.format(self.executable, self.path)


class FastrNotExecutableError(FastrExecutionError):
    """
    The command invoked by subprocess is not executable on the system
    """
    pass


class FastrErrorInSubprocess(FastrExecutionError):
    """
    Encountered an error in the subprocess started by the execution script
    """
    pass


class FastrSubprocessNotFinished(FastrExecutionError):
    """
    Encountered an error before the subprocess call by the execution script was
    properly finished.
    """
    pass


class FastrResultFileNotFound(FastrExecutionError):
    """
    Could not found the result file of job that finished. This means the
    executionscript process was killed during interruption. Generally this
    means a scheduler killed it because of resource shortage.
    """
    pass


class FastrOutputValidationError(FastrExecutionError):
    """
    An output of a Job does not pass validation
    """
    pass


class FastrNoValidTargetError(FastrKeyError):
    """
    Cannot find a valid target for the tool
    """
    pass


class FastrCollectorError(FastrError):
    """
    Cannot collect the results from a Job because of an error
    """
    pass


class FastrPluginCapabilityNotImplemented(FastrNotImplementedError):
    """
    A plugin did not implement a capability that it advertised.
    """
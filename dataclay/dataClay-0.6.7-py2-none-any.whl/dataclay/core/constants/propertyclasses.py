from dataclay.core.properties import PropertyFile
import os.path

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class LangCodes(PropertyFile):
    """Property holder for the "langcodes.properties" file."""
    def __init__(self, property_path, lang_code_name='langcodes.properties'):
        super(LangCodes, self).__init__(os.path.join(property_path, lang_code_name))

    def _process_line(self, key, value):
        """The language codes are simple integer values."""
        self.__dict__[key] = int(value)


class PythonTypeSignatures(PropertyFile):
    """Property holder for the "python_type_signatures.properties" file."""
    def __init__(self, property_path, python_type_name='python_type_signatures.properties'):
        super(PythonTypeSignatures, self).__init__(os.path.join(
            property_path, python_type_name))

    def _process_line(self, key, value):
        """The signatures are plain strings."""
        self.__dict__[key] = value


class MethodIds(PropertyFile):
    """Property holder for the "method_ids.properties" file."""
    def __init__(self, property_path, method_ids_name='method_ids.properties'):
        self.methods = dict()
        super(MethodIds, self).__init__(os.path.join(property_path, method_ids_name))

    def _process_line(self, key, value):
        """The method information are three-value tuples.

        Store the number (the most relevant information) as a method and the
        other information in a redundant fashion in another int-key dict.
        """
        fields = value.split(",")
        method_id = int(fields[0])
        self.__dict__[key] = method_id

        if len(fields) == 3:
            # It is a full-fledged method
            self.methods[method_id] = (key, fields[1], fields[2])


class ErrorCodes(PropertyFile):
    """Property holder for the "errorcodes.properties" file."""
    def __init__(self, property_path, error_codes_name="errorcodes.properties"):
        self.error_codes = {}
        super(ErrorCodes, self).__init__(os.path.join(property_path, error_codes_name))

    def _process_line(self, key, value):
        """The error codes are ints, and reverse lookup is useful."""
        error_code = int(value)
        self.__dict__[key] = error_code
        self.error_codes[error_code] = key

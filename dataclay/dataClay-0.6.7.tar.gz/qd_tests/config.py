from pprint import pprint

import dataclay.core.constants as constants


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

if __name__ == "__main__":
    print("LangCodes:")
    pprint(constants.lang_codes.__dict__)

    print("PythonTypeSignatures:")
    pprint(constants.python_type_signatures.__dict__)

    print("MethodIds:")
    pprint(constants.method_ids.__dict__)
    pprint(constants.method_ids.methods)

    print("ErrorCodes:")
    pprint(constants.error_codes.__dict__)
    pprint(constants.error_codes.error_codes)

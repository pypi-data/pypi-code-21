import io
import json
import os
import sys
import traceback

from . import basics

##############################################################################################################
# constants
##############################################################################################################


PATH_PREFIX = '/lod'
INPUT_FILE_LOCATION = os.path.join(PATH_PREFIX, 'in.txt')
OUTPUT_FILE_LOCATION = os.path.join(PATH_PREFIX, 'out.txt')

def _get_valid_identifier_types():
    """
    returns a list of strings that are all the valid types of identifiers.
    """
    res = [a[0] for a in basics.get_shared_truth()['valid_identifier_types']]
    return res

def _get_valid_event_request_names():
    """
    returns a list of strings that are all the valid types of event requests.
    """
    res = [a[0] for a in basics.get_shared_truth()['valid_event_types']]
    return res


##############################################################################################################
# a context manager to take care of logging and error handling
##############################################################################################################


_the_manager = None
class manager:
    """
    Context manager for managing logging and error handling.
    """
    def __init__(self, suppress_exceptions_after_logging_them=False, redirect_stdout_to_log=True):
        global _the_manager
        if _the_manager is None:
            _the_manager = self
        else:
            warning = "only one manager of the LOD library should be created!"
            print(warning)
            raise IOException(warning)
        self.suppress_exceptions_after_logging_them = suppress_exceptions_after_logging_them
        self.error_file = os.path.join(PATH_PREFIX, 'error.txt')
        self.log_file = os.path.join(PATH_PREFIX, 'log.txt')
        self.redirect_stdout_to_log = redirect_stdout_to_log
    def __enter__(self):
        self.log_file_stream = open(self.log_file, 'w')
        self.log_file_stream.__enter__()
        if self.redirect_stdout_to_log:
            self.previous_stdout = sys.stdout
            sys.stdout = self.log_file_stream
        return self
    def __exit__(self, etype, value, exception_traceback):
        try:
            # stop redirecting stdout to the log file
            if self.redirect_stdout_to_log:
                sys.stdout = self.previous_stdout
            # close the log file
            self.log_file_stream.__exit__()
            # make the output available
            make_output_available()
        except Exception:
            if etype is None:
                etype, value, exception_traceback = sys.exc_info()
        finally:
            # log any uncaught exceptions that may have occurred
            if exception_traceback:
                error_message = "%s\n-----\n%s\n-----\n" % (etype, value,)
                with open(self.error_file, 'w') as f:
                    f.write(error_message)
                    traceback.print_tb(exception_traceback, limit=None, file=f)
                # allow the exception to continue
                return self.suppress_exceptions_after_logging_them
            else:
                # no error, so nothing needs to be done
                pass
    def log(self, message):
        """log a message to the log file.
        This file is available via the collab website for inspection, but is not available to other programs running in collab."""
        self.log_file_stream.write(message)
        self.log_file_stream.write('\n')


def log(message):
    """uses the context manager for logging"""
    if _the_manager is None:
        raise IOError("the LOD library's manager needs to be created in order to use logging.")
    _the_manager.log(message)


##############################################################################################################
# input
##############################################################################################################


_input = None
def _get_input():
    """
    parse the input file. This uses a cache, so it only has to be done once.
    """
    global _input
    if _input is None:
        with io.open(INPUT_FILE_LOCATION, 'r', encoding='utf8') as f:
            _input = json.load(f)
    return _input


_object_manager = None
def get_object_manager():
    """
    parse the basics.ObjectManager from the input.
    This holds a history of everything that has happened so far.
    """
    global _object_manager
    if _object_manager is None:
        _object_manager = basics.parse_object_manager(_get_input()['object_manager'])
    return _object_manager


def get_current_step():
    """
    returns an integer indicating the number of the current step in the execution environment.
    """
    return get_object_manager().get_current_step()


def get_own_program_details():
    """
    returns the name, version and id of this program.
    """
    res = basics.parse_identifier(_get_input()['program_identifier'])
    name, version = res.get_program_name_and_version_separately()
    return res, name, version


def get_inputs():
    """
    returns a dictionary mapping argument name to the FileObjects of inputs that were given to this program.
    """
    inputs = _get_input()['inputs']
    res = {}
    for name, val in inputs.items():
        obj = basics.parse_file_object(val)
        obj.file = os.path.join(PATH_PREFIX, obj.file_name)
        res[name] = obj
    return res


def get_event_of_this_execution():
    """
    returns a description of why this Program is running.
    """
    identifier = basics.parse_identifier(_get_input()['event_identifier'])
    res = get_object_manager().get_object_for_identifier(identifier)
    return res


##############################################################################################################
# output
##############################################################################################################


_output_objects = []


def _add_output_object(obj):
    """
    add an object to the Execution Environment.
    """
    global _output_objects
    _output_objects.append(obj)


_output_files_counter = 0
def add_output_file(file_name):
    """
    create an output, to make the results of this program available to other programs and to the Execution Environment.
    you can create multiple outputs, and they will be added in the order in which they were created with this function.
    """
    global _output_files_counter
    global _output_objects
    identifier = basics.create_preliminary_identifier('file')
    creation_index = _output_files_counter
    creation_step = get_current_step()
    res = basics.FileObject(identifier, file_name, creation_step, creation_index)
    res.file = os.path.join(PATH_PREFIX, "out_%d" % _output_files_counter)
    _output_files_counter += 1
    _add_output_object(res)
    return res


def create_tag(symbol):
    """
    creates a new basics.Tag using method chaining.
    Note that this basics.Tag is preliminary and will be rejected by the Execution Environment if the Symbol does not actually exist,
    or is not accessible for this program, or if anything else is wrong.
    """
    tag = basics.TagRequest().symbol(symbol)
    _add_output_object(tag)
    return tag


def request_program_execution(program_identifier, **argument_dict):
    """
    a request to execute a Program.
    This expects a program as its first argument, and files to use as parameters as the rest.
    The program may be identified as an basics.Identifier object,
    as a String displaying the name of the program (in which case the latest version is picked),
    as a String of <name>#<version> (which identifies the version directly),
    or as an integer that is the program's ID (which is unambiguous and includes the version)
    """
    request = basics.ProgramExecutionRequest().program(program_identifier).arguments(**argument_dict)
    _add_output_object(request)
    return request


def request_to_display_message():
    """
    returns a basics.DisplayMessageRequest, which is used for building a message to display to the user,
    with several options that can be added via method chaining.
    """
    request = basics.DisplayMessageRequest()
    _add_output_object(request)
    return request


def create_option(trigger_rule, display, actions, description=None):
    """
    creates an Option and adds it to the list of objects.
    """
    existing_arguments = {}
    option = basics.Option(basics.create_preliminary_identifier('option'), description, trigger_rule, display, actions, existing_arguments)
    _add_output_object(option)
    return option


def make_output_available():
    """
    create the output file and write all previously added messages to the execution environemnt into it.
    This function is called automatically when the context manager closes, but it is possible to call it earlier, too,
    if you are unsure if the program might time out later, so that you can at least output some preliminary results.
    """
    res = {
        'output_objects' : [a.to_json() for a in _output_objects],
    }
    with io.open(OUTPUT_FILE_LOCATION, 'w', encoding='utf8') as f:
        json.dump(res, f, indent=4, ensure_ascii=False)




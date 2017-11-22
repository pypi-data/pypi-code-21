from eureqa import Eureqa
from eureqa.analysis_templates.parameters_values import ParametersValues

import sys,imp,os
import argparse
import tempfile
import warnings
import shutil
import importlib
import zipfile
from cStringIO import StringIO
import traceback
import os

class Analysis_template_execution:
    pass

class LocalFatalException(Exception):
    """
    Class that represents fatal exceptions from the local runner
    """
    pass

class Local_analysis_template_execution(Analysis_template_execution):
    """
    Stubs out the analysis_template_execution to provide the same interface while running locally.

    :param Eureqa eureqa: A eureqa connection.
    :param str parameters: JSON string of parameters.
    """
    def __init__(self, eureqa, parameters=None):
        self.template_id = 'local_template_id'
        self.analysis_id = 'local_analysis_id'
        if parameters is None: parameters = {}

        try:
            self.parameters = ParametersValues._from_json(eureqa, parameters, execution=None).parameters
        except:
            warnings.warn("Invalid ParametersValues expression: %s.  Continuing with no ParametersValues." % repr(parameters))

        self._done = False
        self._eureqa = eureqa
        self._analysis = eureqa.create_analysis('Analysis from analysis template', 'This analysis was run from a local template executor.')
        self._first_fatal_exception = None

    def get_analysis(self):
        return self._analysis

    def update_progress(self, message):
        """ Update progress of the running analysis.

        :param str message: Message to print indicating progress.
        """
        print message

    def _report_completion(self):
        self._done = True
        pass

    def _report_validation_completion(self):
        pass

    def _is_waiting_on_confirmation(self):
        return False

    def _is_done(self):
        return self._done

    def report_fatal_error(self, error):
        """ Report a fatal error of the running analysis.

        :param str error: Message to print indicating progress.
        """
        if (not self._first_fatal_exception):
            self._first_fatal_exception = LocalFatalException(error)
        raise self._first_fatal_exception

    def throw_if_fatal_exception(self):
        """
        Throw any error encountered as a fatal exception
        """
        if self._first_fatal_exception:
            raise self._first_fatal_exception

class analysis_template_runner:
    """
    Bootstrapper for analysis templates. Sets up the environment
    required to invoke the analysis template and then invokes it.
    """
    def __init__(self):
        self.tempdir = None
        self.path_addition = None

    def __del__(self):
        if (self.tempdir):
            shutil.rmtree(self.tempdir)

    def _add_to_python_path(self, addition):
        """ add the specified location to the python path """
        # Put the user module directory on the sys.path list, so that
        # any submodules referenced within it can be found.
        #
        # By putting it on the *end* of sys.path, we prevent users
        # from overriding any modules that are already available on
        # the system by including them in their .zip file.
        self.path_addition = addition # ensure we clean it up
        # It is important to insert the module path in front of other modules
        # so it does not load other things like built-in analysis tempaltes.
        sys.path.insert(0, addition)



    def _invoke_analysis_template(self, main_module, eureqa, template_execution):
        """Driver method for analyis template module execution.

        main_module is the main_module (object) for the analysis
        template (has run_analysis methods defined, etc)

        """
        try:
            validate_parameters = getattr(main_module, 'validate_parameters', None)

            if (validate_parameters and not callable(validate_parameters)):
                raise Exception('validate_parameters is not a function in ' + getattr(main_module, '__name__', 'unknown'))

            # run validate_parameters function
            try:
                if (validate_parameters):
                    validate_parameters(eureqa=eureqa, template_execution=template_execution)

            except:
                template_execution.report_fatal_error(traceback.format_exc())
                template_execution._report_completion()
                return


            # if we are need to wait on user confirmation of
            # validation, poll here Note that isn't a busy loop:
            # non-obviously, calling is_waiting_on_confirmation will
            # enforce a 1 sec delay between calls
            template_execution._report_validation_completion()

            while (template_execution._is_waiting_on_confirmation()):
                pass

            # If there is a template execution with errors (exceptions
            # or reported), it will be either errored or aborted
            if (template_execution._is_done()):
                return

            try :
                create_analysis = getattr(main_module, 'create_analysis')
            except Exception:
                raise Exception('Can not find create_analysis in ' + getattr(main_module, '__name__', 'unknown'))


            if (not callable(create_analysis)):
                raise Exception('create_analysis is not a function in ' + getattr(main_module, '__name__', 'unknown'))

            # run create_analysis function
            try:
                create_analysis(eureqa=eureqa, template_execution=template_execution)
            except:
                template_execution.report_fatal_error(traceback.format_exc())


            template_execution._report_completion()

        except:
            try :
                template_execution.report_fatal_error(traceback.format_exc())
            except:
                pass


    def get_analysis_module_from_template(self, eureqa, template):
        """Retrieves the bytes that represent an analysis template from the
        eureqa server (as base64-encoded .zip file module); then
        function, raising an Exception if an error occurs.

        :param Eureqa eureqa: A eureqa connection.
        :param Template template: The Template object containing the desired analysis.
        """

        self.tempdir = tempfile.mkdtemp()
        zip_file = os.path.join(self.tempdir, "analysis_module.zip")
        main_module_name = template.get_module(zip_file)

        # Extract the .zip file to the local filesystem
        # so that modules containing .so files, etc,
        # can run properly
        with zipfile.ZipFile(zip_file,"r") as zip_f:
            zip_f.extractall(self.tempdir)

        # Remove the .zip file; we're done with it
        os.remove(zip_file)

        self._add_to_python_path(self.tempdir);
        import importlib
        return importlib.import_module(main_module_name)

    def run_args(self, arguments, _local_execution_parameters=None):
        """ Run a template with the provided arguments.

        :param str arguments: Command line-style argument string.
        """
        """ Parses a set of command line arguments and performs the appropriate action """

        parser = argparse.ArgumentParser(prog='run_analysis_template',
                                         description="Nutonian Analysis Template Runner. "
                                         "Invokes an analysis template function either "
                                         "from the command line or from Eureqa itself")

        parser.add_argument('-e', '--url', type=str,
                            help='Base url of Eureqa instance',
                            default='http://localhost:10002')
        parser.add_argument('--save-credentials',
                            dest="save_credentials", action="store_true",
                            help='Save password to the Eureqa API credential store (not encrypted)')
        parser.add_argument('--quiet',
                            action="store_true",
                            help="Suppress interactive and debugging output")
        parser.add_argument('-u', '--user_name', type=str,
                            help='Username for connecting to Eureqa',
                            default='jlpicard')
        parser.add_argument('-p', '--password', type=str,
                            help='Password for connecting to Eureqa',
                            default='Changeme1')
        parser.add_argument('-k', '--api_key', type=str,
                            help='API Key for connecting to Eureqa',
                            default=None)
        parser.add_argument('-o', '--organization', type=str,
                            help='Organization within Eureqa',
                            default='nutonian')

        local_args = parser.add_argument_group("Local-Mode Arguments")
        local_args.add_argument('-m', '--module_name',
                                 help="[Local Mode] The path to the python module (file or directory) to use",
                                 dest="module_name")

        subproc_args = parser.add_argument_group("Subprocess-Mode Arguments")
        subproc_args.add_argument('--session_key', type=str,
                                  help='[Subprocess Mode Only] Credentials to use to connect to Eureqa')
        subproc_args.add_argument('--analysis_template_id', type=str,
                                  help='[Subprocess Mode Only] The template id of the analysis template to invoke')
        subproc_args.add_argument('--execution_id', type=str,
                                  help='[Subprocess Mode Only] The execution id of the analysis template which was invoked')


        args = parser.parse_args(arguments)

        eureqa = Eureqa(url=args.url, user_name=args.user_name, password=args.password, key=args.api_key, save_credentials=args.save_credentials,
                        organization=args.organization, verify_ssl_certificate=False, session_key=args.session_key, interactive_mode = not args.quiet)

        # Get the appropriate entrypoint
        local_template_execution = None
        if (args.analysis_template_id):
            template = eureqa._get_analysis_template(args.analysis_template_id)
            template_execution = template._get_execution(args.execution_id)
            analysis_module = self.get_analysis_module_from_template(eureqa, template)
        elif (args.module_name):
            local_template_execution = Local_analysis_template_execution(eureqa, _local_execution_parameters)
            template_execution = local_template_execution
            self._add_to_python_path(args.module_name)
            analysis_module = __import__(args.module_name)
        else:
            raise Exception('Must supply either --module_name or --analysis_template_id')

        # now, run the the method
        self._invoke_analysis_template(analysis_module, eureqa, template_execution)

        if (local_template_execution):
            local_template_execution.throw_if_fatal_exception()


# launch using program arguments if main file
if (__name__ == "__main__"):
    runner = analysis_template_runner()
    runner.run_args(sys.argv[1:])

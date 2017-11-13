import csv
import json
import os
import random
import sys
import time
import requests
import base64

from wesci.params import Params
from wesci.files import Files
from wesci.figures import Figures
from wesci.config import Config


class Logger(object):
    """
    Log python script runs, along with input and output files and params.

    When this module is incorporated in a python script and supplied with
    the proper params, it records the script's code, input params+files,
    output params+files, generates thumbnails of figures, and captures
    other relevant data points for curation and reproducibility of the
    script's results.
    The data is viewable both on a local file, and on We-Sci's web
    platform (currently in closed beta)

    Please email contact@we-sci.com for more info.

    Usage:
    ======
    from matplotlib import pyplot as plt
    import wesci

    logger = wesci.Logger(
        script_file=__file__,
        log_file_prefix="./script"
    )

    # inputs
    a = 3

    logger.add_input_params({'a': a})
    logger.add_input_files({'input_csv': 'input.csv'})
    logger.add_input_files({'input_jpg': 'input.jpg'})

    # do some math
    b = a**2

    plt.plot([1, 2, 3], [4, 5, 6])
    logger.add_output_figure('fig1')

    logger.add_output_files({'output_csv': 'output.csv'})
    logger.add_output_params({'b': b})

    # log
    logger.log()
    """

    DEFAULT_INPUT_PARAMS_NAME = 'input_params'
    DEFAULT_INPUT_FILES_NAME = 'input_files'
    DEFAULT_PARAMS_NAME = 'params'
    DEFAULT_OUTPUT_PARAMS_NAME = 'output_params'
    DEFAULT_OUTPUT_FILES_NAME = 'output_files'
    DEFAULT_LOG_PREFIX = '~/default'
    JUPYTER_CELL_DELIMITER = '#--------------------------------------#'
    FIGURE_DIR_SUFFIX = 'figures'
    CONFIG_FILE_PATH = '~/.wesci.conf'
    AMAZON_API_KEY_ID = 'x-api-key'
    PROD_URL = 'https://api.we-sci.com/v1/assays'
    DEV_URL = 'http://127.0.0.1:5000/v1/assays'
    DATAFRAME_MAX_SIZE = 10

    ########################################################
    # version must be equal the one in VERSION file!!!!!!!!!
    VERSION = '0.6.1'
    ########################################################

    def __init__(self,
                 script_file,
                 log_file_prefix=None):
        """
        script_file -- the script file name (Required)
        log_file_prefix -- the path and prefix of the log file.
            Used to set the location of the log file as well as the prefix.
            When none is provided, the log will be written in the same
            dir as the script being run, with the script's name as the prefix.
            If no script file is provided, it will be written
            to '~/default_wesci_log.csv'.
        """
        super(Logger, self).__init__()

        self.version = self.VERSION
        self.input_params = {}
        self.input_files = {}
        self.params = {}
        self.output_params = {}
        self.output_files = {}
        self.output_figures = {}
        self.log_file_name = Logger.__log_filename(log_file_prefix,
                                                   script_file)
        self.script_file = script_file
        self.code = Logger.__get_code_from_file(script_file)
        self.run_gm_timestamp = int(time.time() * 1000)
        self.run_id = Logger.__generate_run_id(self.run_gm_timestamp)
        self.python_version = Logger.__python_version()
        self.data_for_log = {
            'sdk_version': self.version,
            'run_gm_timestamp': self.run_gm_timestamp,
            'run_id': self.run_id,
            'log_file_name': self.log_file_name,
            'script_file': self.script_file,
            'code': self.code,
            'script_dir': os.getcwd(),
            'assay_type': 'python_%s_script_run' % self.python_version
        }
        self.csv_saver = CSVSaver
        self.conf = Config()
        self.conf.load(os.path.expanduser(self.CONFIG_FILE_PATH))

    def add_input_params(self, input_params):
        """Add input params to be logged.

        Keyword arguments:
        input_params -- a hash in the form of
            {'param1_name': param1_value,
             "param2_name": ...
             ...
            }
        """
        self.input_params.update(Logger.__convert_value_to_hash(
            input_params,
            self.DEFAULT_INPUT_PARAMS_NAME
        ))

    def input_params_start(self, globals):
        """Marks the start of the input params block in the code

        keyword arguments:
        globals: a dict of param names and values. Best to provide this argument with the 'globals()' dict
        """
        self.__params_start(globals.copy(), 'input')

    def input_params_end(self, globals):
        """Marks the end of the input params block in the code.
        Updates the logger's input_params property with the new variables
        allocated within the block

        keyword arguments:
        globals: a dict of param names and values. Best to provide this argument with the 'globals()' dict
        """
        self.__params_end(globals.copy(), 'input')

    def output_params_start(self, globals):
        """Marks the start of the output params block in the code

        keyword arguments:
        globals: a dict of param names and values. Best to provide this argument with the 'globals()' dict
        """
        self.__params_start(globals.copy(), 'output')

    def output_params_end(self, globals):
        """Marks the start of the output params block in the code.
        Updates the logger's output_params property with the new variables
        allocated within the block

        keyword arguments:
        globals: a dict of param names and values. Best to provide this argument with the 'globals()' dict
        """
        self.__params_end(globals.copy(), 'output')

    def __params_start(self, params_dict, params_type='input'):
        setattr(self, '%s_start' % params_type, params_dict)

    def __params_end(self, params_dict, params_type):
        start_att_name = '%s_start' % params_type
        end_att_name = '%s_end' % params_type
        setattr(self, end_att_name, params_dict)
        diff = {}
        start_params = getattr(self, start_att_name, {})
        end_params = getattr(self, end_att_name, {})
        for param in end_params.keys():
            if param in start_params:
                continue
            diff[param] = end_params[param]
        clean_outputs = Params.clean_global_params(diff)
        setattr(self, '%s_params' % params_type, clean_outputs)

    def add_output_params(self, output_params):
        """Add output params to be logged.

        Keyword arguments:
        output_params -- a hash in the form of
            {'param1_name': param1_value,
             "param2_name": ...
             ...
            }
        """
        self.output_params.update(Logger.__convert_value_to_hash(
            output_params,
            self.DEFAULT_OUTPUT_PARAMS_NAME
        ))

    def add_input_files(self, input_files):
        """Add input files to be logged.

        Keyword arguments:
        input_files -- a hash in the form of
            {'file1_name': file1_path,
             "file2_name": ...
             ...
            }
        """
        self.input_files.update(Logger.__convert_value_to_hash(
            input_files,
            self.DEFAULT_INPUT_FILES_NAME
        ))

    def add_output_figure(self, figname, fig = None):
        """Add the current matplotlib figure as an output figure to be logged.

        Keyword arguments:
        figname -- the name under which the current matplotlib figure
            will be logged.
        """
        figdata = Figures.add_output_figure(self.__images_dir(), fig)
        self.output_figures.update({figname: figdata})

    def add_output_files(self, output_files):
        """Add output files to be logged.

        Keyword arguments:
        output_files -- a hash in the form of
            {'file1_name': file1_path,
             "file2_name": ...
             ...
            }
        """
        self.output_files.update(Logger.__convert_value_to_hash(
            output_files,
            self.DEFAULT_OUTPUT_FILES_NAME
        ))

    def log(self, global_params=None):
        """Log current run along with all data fed to We-Sci's Logger.
        Both to the web app and locally

        Keyword arguments:
        params_dict (optional) -- a dictionary mapping param_name to param_value. The recommended usage of this params is
            providing the logger with Python's builtin `globals()`. The global variables will be automatically logged and uploaded by the logger without
            the need to manually provide them with the logger's API.

        Usage:
        logger.log(globals())
        """
        if global_params:
            self.__clean_and_add_params(global_params)
        self.__prepare_data_for_log()
        self.__post_log()
        self.__save_csv()

    def __clean_and_add_params(self, params_dict):
        self.__remove_explicitely_added_params(params_dict)
        params_dict = Logger.__convert_value_to_hash(
            params_dict,
            self.DEFAULT_PARAMS_NAME)
        clean_params_dict = Params.clean_global_params(params_dict)
        self.params.update(clean_params_dict)

    def __remove_explicitely_added_params(self, params_dict):
        explicitly_added_keys = list(self.input_params.keys())
        explicitly_added_keys.extend(list(self.output_params.keys()))
        for key in explicitly_added_keys:
            if key in params_dict:
                params_dict.pop(key)

    def __save_csv(self):
        csv_row = self.__data_for_log_as_csv()
        self.csv_saver.save(self.log_file_name, csv_row)

    def __images_dir(self):
        return '%s_%s' % (Logger.__clean_file_name(self.log_file_name),
                          Logger.FIGURE_DIR_SUFFIX)

    def __print_params(self):
        print("logged for user %s" % self.user_id)
        print("logged the following input params: %s" % self.input_params)
        print("logged the following input files: %s" % self.input_files)
        print("logged the following output params: %s" % self.output_params)
        print("logged the following output files: %s" % self.output_files)
        print("logged the following output figures: %s" % self.output_figures)
        print("run id is %s" % self.run_id)

    def __data_for_log_as_csv(self):
        data_for_log = self.data_for_log
        return [
            data_for_log['run_gm_timestamp'],
            data_for_log['run_id'],
            json.dumps(data_for_log['input_params']),
            json.dumps(data_for_log['input_files']),
            json.dumps(data_for_log['params']),
            json.dumps(data_for_log['output_params']),
            json.dumps(data_for_log['output_files']),
            json.dumps(data_for_log['output_figures']),
            data_for_log['script_file'],
            data_for_log['script_dir'],
            data_for_log['assay_type'],
            data_for_log['sdk_version'],
            data_for_log['code'],
            self.upload_succeeded,
        ]

    @staticmethod
    def __clean_file_name(file_name):
        return os.path.splitext(file_name)[0]

    @staticmethod
    def __output_file_name(log_file_prefix):
        return os.path.expanduser(
            "%s_wesci_log.csv" % Logger.__clean_file_name(log_file_prefix))

    @staticmethod
    def __log_filename(log_file_prefix, script_file):
        if log_file_prefix:
            return Logger.__output_file_name(log_file_prefix)
        if script_file:
            return Logger.__output_file_name(script_file)
        return Logger.__output_file_name(Logger.DEFAULT_LOG_PREFIX)

    @staticmethod
    def __convert_value_to_hash(value, name):
        if isinstance(value, dict):
            return value
        return {name: value}

    @staticmethod
    def __python_version():
        return '%s.%s' % (sys.version_info[0], sys.version_info[1])

    @staticmethod
    def __generate_run_id(run_gm_timestamp):
        # composed of millisecond epoch and a 4 digit random num
        ms_timestamp = run_gm_timestamp
        uuid = random.randint(9, 99)
        run_id = int('%s%s' % (ms_timestamp, uuid))
        return run_id

    @staticmethod
    def __get_code_from_file(script_file):
        if script_file is None:
            return None
        file_extension = os.path.splitext(script_file)[1]
        if file_extension == '.py':
            with open(script_file, 'r') as f:
                data = f.read()
            return data
        if file_extension == '.ipynb':
            return Logger.__parse_jupyter_notebook_code(script_file)

    @staticmethod
    def __parse_jupyter_notebook_code(file_path):
        with open(file_path, 'r') as f:
            notebook_string = f.read()
        notebook_data = json.loads(notebook_string)
        code_segments = []
        cells = notebook_data['cells']
        for cell in cells:
            if cell['cell_type'] != 'code':
                continue
            cell_code = "".join(cell['source'])
            cell_code_with_delimiter_and_line_ending = "%s\n%s\n\n" % (
                Logger.JUPYTER_CELL_DELIMITER, cell_code)
            code_segments.append(cell_code_with_delimiter_and_line_ending)
        code = "".join(code_segments)
        return code.encode('utf8')

    def __image_file(self, thumbnail):
        return '%s/%s.%s' % (self.__images_dir(), thumbnail['hash'],
                             Figures.FIGURE_FORMAT)

    def __thumbnail_data(self, thumbnail):
        with open(self.__image_file(thumbnail), 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode('ascii')

    def __mark_upload_success(self):
        self.upload_succeeded = True

    def __mark_upload_failure(self):
        self.upload_succeeded = False

    def __post_log(self):
        data_for_log = self.data_for_log
        figures_data = {
            thumbnail['hash']: self.__thumbnail_data(thumbnail)
            for thumbnail in
            data_for_log['output_figures'].values()
        }
        post_data = {
            'api_key': self.conf.api_key(),
            'assay': json.dumps(data_for_log),
            'figures': figures_data,
        }
        if self.conf.has_secret():
            post_data['secret'] = self.conf.secret()
        # api gateway doesn't like getting
        # files the way requests package handles them
        headers = {self.AMAZON_API_KEY_ID: self.conf.api_key()}
        ret = requests.post(
            Logger.__target_url(),
            headers=headers,
            json=post_data)
        if ret.ok:
            self.__mark_upload_success()
        if not ret.ok:
            self.__mark_upload_failure()
            if ret.status_code == 403:
                self.__print_unauthorized_error()
                return
            req_id = ret.headers['x-amzn-requestid']
            self.__print_post_error(req_id)

    @staticmethod
    def __print_post_error(req_id):
            print("---------------------------------------------------------------")
            print("Log failed, please email support@we-sci.com the following data:")
            print("request id = %s" % req_id)
            print("---------------------------------------------------------------")

    @staticmethod
    def __print_unauthorized_error():
        print("---------------------------------------------------------------")
        print("Your API key seems invalid")
        print("Please check your welcome email or contact support@we-sci.com")
        print("---------------------------------------------------------------")

    @staticmethod
    def __generate_params_data_for_log(params_dict):
        return Params.generate_data_for_log(params_dict)

    @staticmethod
    def __generate_files_data_for_log(files_dict):
        return Files.generate_data_for_log(files_dict)

    def __prepare_data_for_log(self):
        self.data_for_log.update({
            'input_params': Logger.__generate_params_data_for_log(
                self.input_params),
            'input_files': Logger.__generate_files_data_for_log(
                self.input_files),
            'params': Logger.__generate_params_data_for_log(
                self.params),
            'output_params': Logger.__generate_params_data_for_log(
                self.output_params),
            'output_files': Logger.__generate_files_data_for_log(
                self.output_files),
            'output_figures': self.output_figures,
        })

    @staticmethod
    def __target_url():
        is_dev_env = os.environ.get('ENV', 'prod') == 'dev'
        if is_dev_env:
            return Logger.DEV_URL
        return Logger.PROD_URL


class CSVSaver(object):
    @staticmethod
    def save(output_file_name, csv_row):
        with open(output_file_name, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(csv_row)

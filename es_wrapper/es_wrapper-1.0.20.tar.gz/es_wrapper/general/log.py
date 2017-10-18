from queue import Queue
from datetime import datetime
from logging.handlers import RotatingFileHandler
import json
import logging
from optparse import OptionParser
import os
import socket
import sys
import threading
from logstash_formatter import LogstashFormatterV1


EXC_LOGGER = "system_log"
DEFAULT_SYS_LOGGER_NAME = "system_log"


class LoggerInfo:
    """
    Used to get the Loggers name
    """
    name = DEFAULT_SYS_LOGGER_NAME

    def __init__(self):
        pass


def ensure_dir(dir_name):
    """
    Ensures that a named directory exists; if it does not, attempt to create it.

    :param string dir_name: The name of the directory to check
    """
    try:
        os.makedirs(dir_name)
    except OSError as e:
        if e.errno != socket.errno.EEXIST:
            raise


def path_setup(root, name):
    """
    Creates a valid path for a new directory from the path root, verifies it exists
    :param string root: The path of the needed folder
    :param string name: The name of the folder
    :return string file_path: The path to the create folder
    """
    file_path = os.path.join(root, name)
    # Make sure the folder exists
    ensure_dir(file_path)
    return file_path


def logger_setup(file_name, file_path, debug_mode, log_to_file, log_to_kafka):

    """
    The method creates a logger based on a path for the log file and the logger name
    :param string file_path: the path of the log file
    :param string file_name: the name of the Logger
    :param bool debug_mode: True to print log entries to console, False to disable
    :param bool log_to_file: If True we save log messages to a file
    :param bool log_to_kafka: If True we send log messages to Kafka
    :return Logger(file_name):
    """

    # Set up logging
    logger = logging.getLogger(file_name)
    if debug_mode:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Add the log message handler to the logger
    date_tag = datetime.now().strftime("%Y-%b-%d_%H-%M-%S")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    if log_to_file:

        # Create logs folder if it doesnt exist
        ensure_dir(file_path)

        file_name = file_path + file_name + "-" + date_tag + ".log"
        # add a rotating handler
        fh = RotatingFileHandler(file_name,
                                 maxBytes=1024*1024*5,  # 5MB
                                 backupCount=5)
        fh.setLevel(logging.INFO)
        # fh = logging.FileHandler(filename=file_path+file_name + "-" + date_tag + ".log")
        if debug_mode:
            fh.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers

        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # In case we want a console handler as well
    if debug_mode:
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)


    return logger


def sys_logging_setup(log_name, log_params_dict):
    """
    setup necessary parameters for each log
    :param string log_name: the name of the log we wish to create
    :param dict log_params_dict: A dictionary of logging options parameters
    :return: Logger(log_name): And instance of the logger
    """
    try:
        params_tuple = log_params_dict[log_name]
        folder = params_tuple[0]
        console_on = params_tuple[1]
        log_to_file = params_tuple[2]
        log_to_kafka = params_tuple[3]
        return logger_setup(log_name, folder, console_on, log_to_file, log_to_kafka)
    except KeyError:
        raise ValueError("Wrong Log name %s" % log_name)


def init_all_system_logs(module_name, debug_mode=False, project_path="", log_to_file=True, log_to_kafka=True):
    """
    This method initializes all the necessary system logs.
    :param str module_name:
    :param bool debug_mode:
    :param str project_path:
    :param bool log_to_file:
    :param bool log_to_kafka:
    """
    if not project_path and log_to_file:
        project_path = get_project_path_from_args()

    # Set the logger name
    LoggerInfo.name = module_name

    # Loggers
    sys_logger_folder = ""
    if log_to_file:
        logger_folder = path_setup(project_path, 'logs/')
        sys_logger_folder = path_setup(logger_folder, 'sys_logs/')

    log_params = {module_name: (sys_logger_folder, debug_mode, log_to_file, log_to_kafka)}

    # Setup the system logs
    sys_logging_setup(module_name, log_params)

    sys.excepthook = log_uncaught_exception

    logging.Logger.name = module_name


def log_uncaught_exception(type, value, tb):
    logger = logging.getLogger(EXC_LOGGER)
    logger.exception("Uncaught exception: %s %s %s" % (type, value, tb))


def get_project_path_from_args():
    """
    Used in calling the project, getting a source as an argument for the logs
    :return string project_path: A path for the project to write log files
    """
    optp = OptionParser()
    optp.version = '%%prog 0.1'
    optp.usage = "Usage: %%prog <project_path> [options] "
    opts, args = optp.parse_args()

    # Make sure we received enough input args
    if len(args) < 1:
        optp.print_help()
        exit()

    # Take the folder path from the options
    project_path = args[0]

    return project_path


# Log
LOG_TYPE_INFO = 1
LOG_TYPE_ERROR = 2
LOG_TYPE_DEBUG = 3

LOG_SEVERITY_LOW = 1
LOG_SEVERITY_MEDIUM = 2
LOG_SEVERITY_HIGH = 3
LOG_SEVERITY_CRITICAL = 4


def create_log_message(source, source_id, message, severity=LOG_SEVERITY_LOW, log_type=LOG_TYPE_INFO):
    """
    This method returns a dictionary as the log format to save
    :param str source:
    :param str source_id:
    :param str message:
    :param str severity:
    :param str log_type:
    :return str:
    """
    log_message = {"@timestamp": current_utc_time(),
                   "name": "RG",
                   "module": "RG",
                   "source": source,
                   "sourceId": source_id,
                   "msg": message,
                   "severity": severity,
                   "logType": log_type}

    return json.dumps(log_message)


class KafkaLoggingHandler(logging.Handler):

    def __init__(self, hosts_list, topic, key=None):
        # Make sure we can connect to kafka
        self.kafka_client = KafkaClient(hosts_list)

        logging.Handler.__init__(self)

        self.key = key
        self.kafka_topic_name = topic
        self.queue = Queue()

        if not key:
            self.producer = SimpleProducer(self.kafka_client)
        else:
            self.producer = KeyedProducer(self.kafka_client)

        self.kafka_t = threading.Thread(target=self.queue_handler)
        self.kafka_t.setDaemon(True)
        self.kafka_t.start()

    def emit(self, record):
        """
        Called when sending new message to the queue, add messages to the queue for async operation
        :param record: The record to format
        """
        # drop kafka logging to avoid infinite recursion
        if record.name == 'kafka':
            return

        # use default formatting
        msg = self.format(record)

        # Add the message to the queue
        self.queue.put(msg)

    def queue_handler(self):
        """
        The method runs over the kafka queue and emits waiting messages
        """
        while True:
            msg = self.queue.get(block=True)  # blocks
            try:
                if not self.key:
                    self.producer.send_messages(self.kafka_topic_name, msg)
                else:
                    self.producer.send(self.kafka_topic_name, self.key, msg)
            except (KafkaUnavailableError, ):
                pass
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                pass
                # self.handleError(record)

    def close(self):
        """
        Called when system exists to kill the handler
        """
        if self.producer:
            self.producer.stop()
        if self.kafka_t:
            self.kafka_t.join(0.1)
        logging.Handler.close(self)

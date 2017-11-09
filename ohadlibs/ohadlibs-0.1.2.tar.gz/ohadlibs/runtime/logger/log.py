import datetime
from collections import OrderedDict
import os


class Log:

    def __init__(self, log_name, logs_dir):
        """
        Basic log object that creates logs in a dedicated folder.
        :param log_name: string
        """
        self.name = "{}_{}".format(log_name, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        log_dirs = OrderedDict()
        log_dirs['logs_dir'] = logs_dir
        log_dirs['log_dir'] = os.path.join(log_dirs['logs_dir'], self.name)
        [os.mkdir(log_dirs[directory]) for directory in log_dirs if not os.path.exists(log_dirs[directory])]

        self.main_dir = log_dirs['log_dir']
        self.main_log = open(os.path.join(self.main_dir, "main.log"), 'w')

    def log(self, message):
        log_message = "[{}] {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
        print log_message
        self.main_log.write("{}\n".format(log_message))


if __name__ == '__main__':
    log = Log("ohad_test", "logs")
    log.log("Ahalan")
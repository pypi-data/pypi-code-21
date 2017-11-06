from fluent import sender
from fluent import event
import datetime

#sender.setup('fluentd.test', host='localhost', port=24224)

import logging.config
import yaml

from fluent import handler
import os.path

class Logger:
    # def __init__(self,host,port,name):
    #     self.host = host
    #     self.port = port
    #     self.name = name
    #     sender.setup('fluentd.justpith', host=self.host, port=self.port)
    #
    # def log(self,message,source):
    #     time  = datetime.datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')
    #     output = {
    #         "time": time,
    #         "output": message,
    #         "source": source
    #     }
    #     event.Event(self.name, output)

    def __init__(self,host=None,port=None,name=None,level=None):

        self.host = host
        self.port = port
        self.name = name
        self.absolute_path = os.path.abspath(os.path.dirname(__file__))
        self.config_file = self.absolute_path + "/logging.yaml"
        if self.name == 'controller' or self.name == 'server' or self.name == 'parser' or self.name == 'rss_consumer' or self.name == 'teacher' or self.name == 'teacher_consumer' or self.name == 'reccomender' or self.name == 'reccomender_consumer' or self.name == 'news_consumer' or self.name == 'controller_consumer' or self.name == 'matrix':
            pass
        else:
            raise Exception

        if level is None:
            self.level = logging.INFO
        elif level == "WARNING":
            self.level = logging.WARNING
        elif level == "DEBUG":
            self.level = logging.DEBUG
        elif level == "ERROR":
            self.level = logging.ERROR
        elif level == "CRITICAL":
            self.level = logging.CRITICAL
        elif level == "INFO":
            self.level = logging.INFO

        self.logger = None

        with open(self.config_file) as fd:
            conf = yaml.load(fd)
            logging.config.dictConfig(conf['logging'])

        # se non e'specificato host o port si usa il config cosi' come e'
        # viene cambiato solo il level se e' stato specificato
        if self.host is None or self.port is None:
            self.logger = logging.getLogger(self.name)
            if self.level is not None:
                self.logger.setLevel(self.level)
        else:

        # se invece abbiamo host e port si crea un handler apposito con host,post nuove
        # si crea un formatter uguale a quello del config, si aggiunge il formatter all handler
        # si attacca l'handler al logger che si prende dal config

            custom_format = {
                'host': '%(hostname)s',
                'where': '%(module)s.%(funcName)s',
                'type': '%(levelname)s',
                'stack_trace': '%(exc_text)s',
                # 'message': '%(message)s'
            }

            self.logger = logging.getLogger(self.name)
            if self.level is not None:
                self.logger.setLevel(self.level)
            else:
                self.logger.setLevel(logging.INFO)

            h = handler.FluentHandler('fluentd.justpith', host=self.host, port=self.port)
            formatter = handler.FluentRecordFormatter(custom_format)
            h.setFormatter(formatter)
            self.logger.addHandler(h)

    def log(self, message, source, level=None):
        time  = datetime.datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')


        output = {
            #"time": time,
            "output": message,
            "source": source
        }

        if level is None:
            self.logger.info(output)
        elif level == "WARNING":
            self.logger.warning(output)
        elif level == "DEBUG":
            self.logger.debug(output)
        elif level == "ERROR":
            self.logger.error(output)
        elif level == "CRITICAL":
            self.logger.critical(message)
        elif level == "INFO":
            self.logger.info(output)

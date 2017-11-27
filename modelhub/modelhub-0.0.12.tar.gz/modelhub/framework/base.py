# encoding=utf8
# author=spenly
# mail=i@spenly.com

from abc import ABCMeta, abstractmethod, abstractproperty
import datetime
import logging
import logging.config
from modelhub.utils import json
from modelhub.core import conf

class BaseModel(metaclass=ABCMeta):
    TYPE = "NTF"  # choose from 'TF' or 'NTF': TensorFlow-based or not

    @abstractproperty
    def model_name(self):
        raise NotImplementedError

    def __init__(self, verbose=False, **kwargs):
        self.__dict__.update(kwargs)
        self.verbose = verbose
        logging.config.dictConfig(conf.LOG_CONFIG)
        self.logger = logging.getLogger("api_model")
        if self.verbose:
            self.logger.setLevel(logging.DEBUG)
        self.prepare()

    @abstractmethod
    def prepare(self):
        """
        # must have, rewrite
        prepare models/datasets only once
        :return:
        """
        pass

    @abstractmethod
    def is_ready(self):
        """
        # must have, rewrite
        check preparation above before running
        :return: True or False
        """
        pass

    def preprocess(self, raw_input):
        """
        # optional
        preprocess data
        :param raw_input: input data in a dict format (may have a nested structure in values) from API Platform
        :return: preprocessed data, define data structure as you prefer
        """
        return raw_input

    @abstractmethod
    def run_model(self, preprocessed_data):
        """
        # must have, rewrite
        run model to do inference
        :param preprocessed_data: preprocessed data
        :return: inferred data, define data structure in your model. We recommend using a dict structure
            (may have a one-layer nested structure in values) to store results.
            This may output to API Platform directly without post-processing.
        """
        raise NotImplementedError

    def postprocess(self, result, raw_input, preprocessed_data):
        """
        # optional
        postprocess inferred data
        :param result: result
        :param raw_input: user input before preprocessing
        :param preprocessed_data: input after preprocessing
        :return: output data in a dict format (may have a one-layer nested structure in values) to API Platform
        """
        return result

    def run(self, raw_input):
        """
        # must have
        run function
        :param raw_input: data
        :return: result
        """
        self.validate_input_data(raw_input)
        preprocessed_data = self.preprocess(raw_input)
        inferenced_data = self.run_model(preprocessed_data)
        return self.postprocess(inferenced_data, raw_input, preprocessed_data)

    @abstractmethod
    def docstring(self):
        """
        # must have, rewrite
        docstring for running function
        :return: docs
        """
        docs = """
        inputs:
            type: string
            description: text string
            default: 
                        text: "your input string" 
        outputs:
            type: array
            description: result list
            default:
                -   val1: "value"
                    val2: 2
        """
        return docs

    class InvalidValueInput(Exception):
        pass

    @abstractmethod
    def validate_input_data(self, raw_input):
        "raise BaseModel.InvalidValueInput if input is not expected"
        pass

    def log_info(self, msg, *args, **kwargs):
        """
        log a message, more details to see logging.info()
        """
        self.logger.info(msg, *args, **kwargs)

    def log_error(self, msg, *args, **kwargs):
        """
        log a message, more details to see logging.error()
        """
        self.logger.error(msg, *args, **kwargs)

    def log_debug(self, msg, *args, **kwargs):
        """
        log a message, more details to see logging.debug()
        """
        self.logger.debug(msg, *args, **kwargs)

    def log_warning(self, msg, *args, **kwargs):
        """
        log a message, more details to see logging.warning()
        """
        self.logger.warning(msg, *args, **kwargs)

    def log_exception(self, msg, *args, **kwargs):
        """
        log a message, more details to see logging.exception()
        """
        self.logger.exception(msg, *args, **kwargs)

    def log_critical(self, msg, *args, **kwargs):
        """
        log a message, more details to see logging.critical()
        """
        self.logger.critical(msg, *args, **kwargs)

    def _run_dict(self, data):
        result = self.run(data)
        return json.loads(json.dumps(result))

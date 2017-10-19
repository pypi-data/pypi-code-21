#! /usr/bin/python3
from flask import Flask
from flask_cors import CORS
from magen_rest_apis.magen_app import CustomJSONEncoder
from magen_utils_apis.singleton_meta import Singleton
from magen_utils_apis.magen_flask_response import JSONifiedResponse

__author__ = "paulq@cisco.com"
__maintainer__ = "Alena Lifar"
__email__ = "alifar@cisco.com"
__copyright__ = "Copyright(c) 2017, Cisco Systems, Inc."
__version__ = "0.4.1"
__status__ = "alpha"


class MagenKeyServerApp(metaclass=Singleton):

    def __init__(self):
        _KeyServerFlask = type('KeyServerFlask', (Flask,), {'response_class': JSONifiedResponse})
        self.__app = _KeyServerFlask(__name__)
        self.__app.json_encoder = CustomJSONEncoder
        CORS(self.__app)

    @property
    def app(self):
        return self.__app

    @app.setter
    def app(self, value):
        pass

# -*- coding: utf-8 -*-
"""
Example

class Client(TFBaseClient):
    model_name="language_detect"
"""


from .base import BaseClient
from abc import abstractproperty


class TFBaseClient(BaseClient):

    def __init__(self, hostport):
        self.hostport = hostport

    @abstractproperty
    def model_name(self):
        pass

    def prepare(self):
        pass

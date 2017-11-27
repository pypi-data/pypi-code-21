# -*- coding: utf-8 -*-


class ValidationException(Exception):
    def __init__(self, value=None):
        self.value = value
    def __str__(self):
        if type(self.value) == unicode \
                or type(self.value) == str \
                or type(self.value) == dict:
            return self.value
        return repr(self.value)


from __future__ import absolute_import, division, print_function

# the Error object for some setup failure


class SetupError(Exception):
    def __init__(self, msg):
        self.__msg = msg

    def __str__(self):
        return self.__msg

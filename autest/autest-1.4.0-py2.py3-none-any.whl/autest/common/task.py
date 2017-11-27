from __future__ import absolute_import, division, print_function
from .constructor import call_base, smart_init


@smart_init
class Task(object):

    @call_base()
    def __init__(self, callback):
        self.__func = callback

    def run(self):
        host.VerboseMessage(['task'], "Starting Task")
        try:
            ret = self.__func()
        except KeyboardInterrupt:
            raise
        except:
            # something went wrong...
            ret = 1
        host.VerboseMessage(['task'], "Task Finished")
        return ret

import time

import chainlet


@chainlet.funclet
def delay(value, duration):
    """
    Pause a chain for ``duration`` seconds

    :param value: arbitrary data chunk
    :param duration: seconds to pause chain execution
    :type duration: int or float
    :return:
    """
    time.sleep(duration)
    return value


class Every(chainlet.ChainLink):
    """
    Pass on only every nth value

    :param nth: the repeating index of the data chunk to pass on
    :param first: how many chunks to wait before passing on the first
    """
    def __init__(self, nth=10, first=0):
        self.nth = nth
        self._count = 0 - first

    def chainlet_send(self, value=None):
        count = self._count = self._count + 1
        if count % self.nth == 1 and count > 0:
            return value
        raise chainlet.StopTraversal

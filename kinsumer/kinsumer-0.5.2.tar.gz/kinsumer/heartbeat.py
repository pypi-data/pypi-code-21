""":mod:`kinsumer.heartbeat` --- Periodic signal generation to indicate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import abc


class Heartbeat(abc.ABC, object):
    """Heartbeat is the interface for signal generation to indicate

    """

    @abc.abstractmethod
    def heartbeat(self):
        """Generate a periodic signal"""

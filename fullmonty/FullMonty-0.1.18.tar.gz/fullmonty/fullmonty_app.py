# coding=utf-8
"""
The FullMonty application.

"""
from fullmonty.graceful_interrupt_handler import GracefulInterruptHandler
from fullmonty.simple_logger import Logger, info, error, FileLogger, debug

__docformat__ = 'restructuredtext en'
__all__ = ("FullMontyApp",)


class FullMontyApp(object):
    """
    This is the application class.

    Usage::

        cli = FullMontyCLI()
        cli.execute(FullMontyApp())

    """

    def __init__(self):
        """
        The FullMonty application.
        """
        # noinspection PyArgumentEqualDefault
        Logger.set_verbose(True)
        Logger.set_debug(False)

    # noinspection PyUnresolvedReferences
    def execute(self, settings):
        """
        Execute the tasks specified in the settings object.

        :param settings: the application settings
        :type settings: argparse.Namespace
        :return: None
        :raises: ArgumentError
        """
        Logger.set_verbosity(settings.verbosity)
        if settings.logfile is not None and settings.logfile:
            Logger.add_logger(FileLogger(settings.logfile))

        with GracefulInterruptHandler() as handler:
            # TODO: implement app here
            pass

        return None

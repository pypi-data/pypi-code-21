# coding=utf-8
"""
The command line interface for the FullMonty application.

"""
from fullmonty.fullmonty_settings import FullMontySettings
from fullmonty.simple_logger import error, info

__docformat__ = 'restructuredtext en'
__all__ = ("ArgumentError", "FullMontyCLI")


class ArgumentError(RuntimeError):
    """There is a problem with a command line argument"""
    pass


class FullMontyCLI(object):
    """
    Command Line Interface for the FullMonty App
    """

    def execute(self, app):
        """
        Handle the command line arguments then execute the app.

        :param app: the application instance
        :type app: fullmonty.FullMontyApp
        """
        with FullMontySettings() as settings:
            try:
                results = app.execute(settings)
                if results is not None:
                    self.report(results)
                exit(0)
            except ArgumentError as ex:
                error(str(ex))
                exit(1)

    # noinspection PyMethodMayBeStatic
    def report(self, results):
        """

        :param results: (success[], error[], missing_filters_for_rule_ids[])
        :type results: tuple
        """
        # TODO: implement result report
        info("Results: {results}".format(results=repr(results)))

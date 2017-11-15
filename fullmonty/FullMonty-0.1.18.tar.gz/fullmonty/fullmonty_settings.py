# coding=utf-8
"""
FullMontySettings adds application specific information to the generic ApplicationSettings class.
"""
from fullmonty.application_settings import ApplicationSettings

__docformat__ = 'restructuredtext en'
__all__ = ("FullMontySettings",)


class FullMontySettings(ApplicationSettings):
    """
    Usage::

        with FullMontySettings() as settings:
        try:
            app.execute(self, settings)
            exit(0)
        except ArgumentError as ex:
            error(str(ex))
            exit(1)
    """
    HELP = {
        'FullMonty': "Eclectic library for applications.",

        'info_group': '',
        'version': "Show FullMonty's version.",
        'longhelp': 'Long help about FullMonty.',

        'output_group': 'Options that control generated output.',
        'verbosity': 'Set verbosity level: 0=none, 1=errors, 2=info+errors, 3+=debug+info+errors (default=2).',
        'logfile': 'File to log all messages (debug, info, warning, error, fatal) to.',
    }

    def __init__(self):
        super(FullMontySettings, self).__init__('FullMonty', 'fullmonty', ['FullMonty'], self.HELP)

    def _cli_options(self, parser, defaults):
        """
        Adds application specific arguments to the parser.

        :param parser: the argument parser with --conf_file already added.
        :type parser: argparse.ArgumentParser
        """
        info_group = parser.add_argument_group(title='Informational Commands', description=self._help['info_group'])
        info_group.add_argument('--version', dest='version', action='store_true', help=self._help['version'])
        info_group.add_argument('--longhelp', dest='longhelp', action='store_true', help=self._help['longhelp'])

        output_group = parser.add_argument_group(title='Output Options', description=self._help['output_group'])
        output_group.add_argument('--verbosity', dest='verbosity', default=2, type=int, metavar='INT',
                                  help=self._help['verbosity'])
        output_group.add_argument('--logfile', type=str, metavar='FILE', help=self._help['logfile'])

    def _cli_validate(self, settings, remaining_argv):
        """
        Verify we have required options for commands.

        :param settings: the settings object returned by ArgumentParser.parse_args()
        :type settings: argparse.Namespace
        :return: the error message if any
        :rtype: str or None
        """
        return None

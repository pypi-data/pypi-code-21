from __future__ import unicode_literals, print_function

import argparse
import os
import sys
import logging
import itertools

from abc import ABCMeta, abstractmethod

from terminaltables import AsciiTable

from qordoba.commands.delete import delete_command
from qordoba.commands.init import init_command
from qordoba.commands.ls import ls_command
from qordoba.commands.pull import pull_command
from qordoba.commands.push import push_command
from qordoba.commands.status import status_command, status_command_json
from qordoba.settings import load_settings, SettingsError
from qordoba.utils import with_metaclass, FilePathType, CommaSeparatedSet
from qordoba.log import init

log = logging.getLogger('qordoba')

try:
    import signal


    def exithandler(signum, frame):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        sys.exit(1)


    signal.signal(signal.SIGINT, exithandler)
    signal.signal(signal.SIGTERM, exithandler)
    if hasattr(signal, 'SIGPIPE'):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

except KeyboardInterrupt:
    sys.exit(1)


class ArgsHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = 'Usage: '
        return super(ArgsHelpFormatter, self).add_usage(usage, actions, groups, prefix)


def fix_parser_titles(parser):
    parser._positionals.title = 'Positional arguments'
    parser._optionals.title = 'Optional arguments'


class BaseHandler(with_metaclass(ABCMeta)):
    name = NotImplemented
    help = None

    def __init__(self, **kwargs):
        super(BaseHandler, self).__init__()
        for k, v in kwargs.items():
            setattr(self, k, v)

        self._curdir = os.path.abspath(os.getcwd())

    def load_settings(self):
        config, loaded = load_settings(access_token=self.access_token,
                                       project_id=self.project_id,
                                       organization_id=self.organization_id)
        config.validate()
        if not loaded:
            log.info('Config not found...')
        return config

    @classmethod
    def register(cls, root, **kwargs):
        kwargs.setdefault('name', cls.name)
        kwargs.setdefault('help', cls.help)
        kwargs['add_help'] = False

        parser = root.add_parser(**kwargs)
        fix_parser_titles(parser)
        parser.set_defaults(_handler=cls)
        parser.add_argument('--project-id', required=False, type=int, dest='project_id',
                            help='The ID of your Qordoba project.',
                            default=None)
        parser.add_argument('--access-token', required=False, type=str, dest='access_token',
                            help='Your Qordoba access token.',
                            default=None)
        parser.add_argument('--organization-id', required=False, type=int, dest='organization_id',
                            help='The ID of your Qordoba organization.',
                            default=None)
        parser.add_argument('--traceback', dest='traceback', action='store_true')
        parser.add_argument('--debug', dest='debug', default=False, action='store_true')
        parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')

        return parser

    def __call__(self):
        self.main()

    @abstractmethod
    def main(self):
        pass


class InitHandler(BaseHandler):
    name = 'init'
    help = """
    Create your .qordoba.yml configuration file.
    """

    def main(self):
        init_command(self._curdir, self.access_token, self.project_id, organization_id=self.organization_id,
                     force=self.force)

    @classmethod
    def register(cls, root, **kwargs):
        kwargs.setdefault('name', cls.name)
        kwargs.setdefault('help', cls.help)
        kwargs['add_help'] = False

        parser = root.add_parser(**kwargs)
        fix_parser_titles(parser)
        parser.set_defaults(_handler=cls)
        parser.add_argument('--organization-id', type=int, required=False, dest='organization_id',
                            help='The ID of your Qordoba organization.')
        parser.add_argument('--access-token', type=str, required=True, dest='access_token',
                            help='Your Qordoba access token.',
                            default=None)
        parser.add_argument('--project-id', type=int, required=True, dest='project_id',
                            help='The ID of your Qordoba project.',
                            default=None)

        parser.add_argument('--traceback', dest='traceback', action='store_true')
        parser.add_argument('--debug', dest='debug', action='store_true')
        parser.add_argument('--force', dest='force', action='store_true')
        parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')


class StatusHandler(BaseHandler):
    name = 'status'
    help = """
    Use the status command to show localization status in current project.
    """
    @classmethod
    def register(cls, *args, **kwargs):
        parser = super(StatusHandler, cls).register(*args, **kwargs)
        parser.add_argument('-j', '--json', dest='json', action='store_true', help='Print json dict to stdout.')
        return parser

    def convert(self, input):
        if isinstance(input, dict):
            return {self.convert(key): self.convert(value) for key, value in input.iteritems()}
        elif isinstance(input, list):
            return [self.convert(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input

    def main(self):
        config = self.load_settings()

        if self.json:
            dict = list(status_command_json(config))
            unidict = self.convert(dict)
            dict_str = str((unidict))
            print(dict_str.replace("'", '"'))
        else:
            rows = list(status_command(config))

            table = AsciiTable(rows).table
            print(table)


class PullHandler(BaseHandler):
    name = 'pull'
    help = """
    Use the pull command to download locale files from the project.
    """

    @classmethod
    def register(cls, *args, **kwargs):
        parser = super(PullHandler, cls).register(*args, **kwargs)
        parser.add_argument('files', nargs='*', metavar='FILE', default=None, help="")
        parser.add_argument('--in-progress', dest='in_progress', action='store_true',
                            help='Allow to download not completed translations.')
        parser.add_argument('-l', '--languages', dest='languages', nargs='+', type=CommaSeparatedSet(),
                            help="Work only on specified (comma-separated) languages.")
        parser.add_argument('-f', '--force', dest='force', action='store_true',
                            help='Force to update local translation files. Do not ask approval.')
        # pull_type_group = parser.add_mutually_exclusive_group()
        parser.add_argument('-b', '--bulk', dest='bulk', action='store_true',
                            help="Force to download languages in bulk, incl. source language.")
        parser.add_argument('-custom', '--custom', dest='custom', action='store_true',
                            help="Allows to pull file with custom extension provided in config files")
        parser.add_argument('-w', '--workflow', dest='workflow', action='store_true',
                            help="Force to download files from a specific workflow step.")
        parser.add_argument('-wa', '--workflow-all', dest='workflow_all', default=None, type=str,
                            help="Force to download ALL files from a specific workflow step.")
        parser.add_argument('-d', '--distinct', dest='distinct', action='store_true',
                            help="Allows you to pull distinct filenames.")
        parser.add_argument('--version', dest='version', default=None, type=str, help="Set version tag.")
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--skip', dest='skip', action='store_true', help='Skip downloading if file exists.')
        group.add_argument('--replace', dest='replace', action='store_true', help='Replace existing file.')
        group.add_argument('--set-new', dest='set_new', action='store_true',
                           help='Ask to set new filename if file exists.')

        return parser

    def get_update_action(self):
        action = None
        if self.skip:
            action = 'skip'
        elif self.replace:
            action = 'replace'
        elif self.set_new:
            action = 'set_new'
        return action

    def main(self):
        log.info('Loading Qordoba config...')
        config = self.load_settings()
        languages = []
        if isinstance(self.languages, (list, tuple, set)):
            languages.extend(self.languages)

        pull_command(self._curdir, config, files=self.files, languages=set(itertools.chain(*languages)),
                     in_progress=self.in_progress, update_action=self.get_update_action(), force=self.force, custom=self.custom, bulk=self.bulk, version=self.version, workflow=self.workflow, workflow_all=self.workflow_all, distinct=self.distinct)


class PushHandler(BaseHandler):
    name = 'push'
    help = """
    Use the push command to upload your resource files to the project.
    """

    def load_settings(self):
        config = super(PushHandler, self).load_settings()
        config.validate(keys=('organization_id',))
        return config

    @classmethod
    def register(cls, *args, **kwargs):
        parser = super(PushHandler, cls).register(*args, **kwargs)
        parser.add_argument('files', nargs='*', metavar='PATH', default=None, type=FilePathType(), help="")
        parser.add_argument('--update', dest='update', default=False, action='store_true', help="Force to update file.")
        parser.add_argument('--version', dest='version', default=None, type=str, help="Set version tag.")
        return parser

    def main(self):
        log.info('Loading Qordoba config...')
        config = self.load_settings()
        push_command(self._curdir, config, update=self.update, version=self.version, files=self.files)

class ListHandler(BaseHandler):
    name = 'ls'
    help = """
    Use the ls command to show all resources that have been initialized under the local project.
    """

    def main(self):
        log.info('Loading Qordoba config...')
        rows = [['ID', 'NAME', '#SEGMENTS', 'UPDATED_ON', 'STATUS'], ]
        rows.extend(ls_command(self.load_settings()))

        table = AsciiTable(rows).table
        print(table)

class DeleteHandler(BaseHandler):
    name = 'delete'
    help = """
    Use the delete command to delete any resource and its translations.
    """

    def load_settings(self):
        config = super(DeleteHandler, self).load_settings()
        config.validate(keys=('organization_id',))
        return config

    @classmethod
    def register(cls, *args, **kwargs):
        parser = super(DeleteHandler, cls).register(*args, **kwargs)
        parser.add_argument('file', default=(), type=str,
                            help="Define resource name or ID.")
        parser.add_argument('-f', '--force', dest='force', action='store_true', help='Force delete resources.')
        return parser

    def main(self):
        log.info('Loading Qordoba config...')
        config = self.load_settings()
        delete_command(self._curdir, config, self.file, force=self.force)


from commands.i18n_extract import extract

class ExtractHandler(BaseHandler):
    name = 'i18n-extract'
    help = """
    Give the i18n-extract command your directory path. It will extract all the stringliterals from your project.
    """

    @classmethod
    def register(cls, *args, **kwargs):
        parser = super(ExtractHandler, cls).register(*args, **kwargs)
        fix_parser_titles(parser)
        parser.set_defaults(_handler=cls)
        parser.add_argument("-i", "--input", type=str, required=True)
        parser.add_argument("-o", "--output", type=str, required=True)
        parser.add_argument("-l", "--lexer_custom", type=str, required=False)
        parser.add_argument("-b", "--bulk_report", required=False)

    def main(self):
        log.info('Starting extraction...')
        extract(self._curdir, input=self.input, output=self.output, lexer_custom=self.lexer, bulk_report=self.bulk_report)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="""
        The Qordoba CLI allows you to manage your localization files.
        Using Qordoba CLI, you can pull and push content from within your own application.
        """,
        formatter_class=ArgsHelpFormatter,
        add_help=False
    )
    parser._positionals.title = 'Positional arguments'
    parser._optionals.title = 'Optional arguments'
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                        help='Show this help message and exit.')

    subparsers = parser.add_subparsers()
    args = {
        'formatter_class': ArgsHelpFormatter
    }

    InitHandler.register(subparsers, **args)
    StatusHandler.register(subparsers, **args)
    PullHandler.register(subparsers, **args)
    PushHandler.register(subparsers, **args)
    ListHandler.register(subparsers, **args)
    DeleteHandler.register(subparsers, **args)
    ExtractHandler.register(subparsers, **args)

    args = parser.parse_args()
    return args, parser


def main():
    args, root = parse_arguments()
    if not hasattr(args, '_handler'):
        root.print_help()
        return

    else:
        log_level = logging.DEBUG if args.debug else logging.INFO
        init(log_level, traceback=args.traceback)
        cli_handler = args._handler(**vars(args))

    try:
        cli_handler()
    except Exception as e:
        log.critical(e)
        if args.traceback:
            import traceback
            traceback.print_exc()

        sys.exit(1)


if __name__ == '__main__':
    main()

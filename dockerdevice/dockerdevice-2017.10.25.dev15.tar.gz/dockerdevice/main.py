import sys
import os
from os import environ
from cliff.app import App
from cliff.commandmanager import CommandManager
from dockerdevice import version

import warnings
warnings.filterwarnings("ignore")

import logging
logging.getLogger("requests").setLevel(logging.WARNING)

class DockerDeviceApp(App):

    def __init__(self, **kwargs):
        super(DockerDeviceApp, self).__init__(description='dockerdevice', version=version.__version__,
                                          command_manager=CommandManager('dockerdevice.client'), **kwargs)

    def build_option_parser(self, description, version, argparse_kwargs=None):
        '''
        Introduces global arguments for the application.
        This is inherited from the framework.
        '''
        parser = super(DockerDeviceApp, self).build_option_parser(
            description, version, argparse_kwargs)
        return parser

    def initialize_app(self, argv):
        self.LOG.debug('initialize_app')


    def prepare_to_run_command(self, cmd):
        self.LOG.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.LOG.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.LOG.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    app = DockerDeviceApp()
    return app.run(argv)


if __name__ == '__main__':
	sys.exit(main(sys.argv[1:]))

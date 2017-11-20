"""Plumbum CLI wrapper for easier/common application writing"""
import platform

from plumbum import cli

import prosper.common.prosper_logging as p_logging
import prosper.common.prosper_config as p_config


class ProsperApplication(cli.Application):
    """parent-wrapper for CLI applications"""

    debug = cli.Flag(
        ['d', '--debug'],
        help='DEBUG MODE: do not write to prod'
    )

    verbose = cli.Flag(
        ['v', '--verbose'],
        help='enable verbose messaging'
    )

    def __new__(cls, *args, **kwargs):
        """wrapper for ensuring expected variables"""
        if not hasattr(cls, 'config_path'):
            raise NotImplementedError(
                '`config_path` required path to default .cfg file'
            )
        return super(cli.Application, cls).__new__(cls)  # don't break cli.Application

    @cli.switch(
        ['--config'],
        str,
        help='Override default config')
    def override_config(self, config_path):
        """override config object with local version"""
        self.config_path = config_path

    @cli.switch(
        ['--dump-config'],
        help='Dump default config to stdout')
    def dump_config(self):
        """dumps configfile to stdout so users can edit/implement their own"""
        with open(self.config_path, 'r') as cfg_fh:
            base_config = cfg_fh.read()

        print(base_config)
        exit()

    _logger = None
    @property
    def logger(self):
        """uses "global logger" for logging"""
        if self._logger:
            return self._logger
        else:
            log_builder = p_logging.ProsperLogger(
                self.PROGNAME,
                self.config.get('LOGGING', 'log_path'),
                config_obj=self.config
            )

            if self.debug:
                log_builder.configure_debug_logger()
            else:
                id_string = '({platform}--{version})'.format(
                    platform=platform.node(),
                    version=self.VERSION
                )
                if self.config.get('LOGGING', 'discord_webhook'):
                    log_builder.configure_discord_logger(
                        custom_args=id_string
                    )
                if self.config.get('LOGGING', 'slack_webhook'):
                    log_builder.configure_slack_logger(
                        custom_args=id_string
                    )

            self._logger = log_builder.get_logger()
            return self._logger

    _config = None
    @property
    def config(self):
        """uses "global config" for cfg"""
        if self._config:
            return self._config
        else:
            self._config = p_config.ProsperConfig(self.config_path)
            return self._config

class ProsperTESTApplication(ProsperApplication):
    """test wrapper for CLI tests"""
    from os import path
    PROGNAME = 'CLITEST'
    VERSION = '0.0.0'

    HERE = path.abspath(path.dirname(__file__))

    config_path = path.join(HERE, 'common_config.cfg')

    def main(self):
        """do stuff"""
        self.logger.info('HELLO WORLD')

if __name__ == '__main__':
    ProsperTESTApplication.run()  # test hook

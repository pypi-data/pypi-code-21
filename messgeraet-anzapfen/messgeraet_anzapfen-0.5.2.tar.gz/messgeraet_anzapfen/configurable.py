"""
    COPYRIGHT (C) 2017 by Sebastian Stigler

    NAME
        configurable.py -- Baseclass for configurable classes

    FIRST RELEASE
        2017-07-05  Sebastian Stigler  sebastian.stigler@hs-aalen.de

"""
import logging

_logger = logging.getLogger(__name__)

__all__ = ['Configurable']


class Configurable:
    """A base class/mixin which can be used to add confighandling to a class"""

    # Add a list of keys that the config should have
    config_keys = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = None

    def load_config(self, config):
        """Load the section of the config for the class

           It is expected that the config contains a section named exactly
           like the class name.

           Will raise a KeyError if there is no such section in the config"""

        section = self.__class__.__name__
        _logger.debug("Load section %s of the config. " % section)
        self.config = config[section]
        self._check_config()

    def _check_config(self):
        """check self.config if the necessary keys are in this section.

           Will raise a NotImplementedError if the class variable
           config_keys is missing.

           Will raise a KeyError if there is a missing entry"""

        config_keys = self.__class__.config_keys

        if config_keys is None or not isinstance(config_keys, list):
            raise NotImplementedError('You have to set the class variable '
                                      '"config_key" to a list of stings which '
                                      'are expected in the current section of '
                                      'the config file.')
        for key in config_keys:
            if key not in self.config:
                raise KeyError(('The key "%s" is not in the section "%s" of '
                                'the config file') % (key, self.config.name))

# vim: ft=python ts=4 sta sw=4 et ai
# python: 3

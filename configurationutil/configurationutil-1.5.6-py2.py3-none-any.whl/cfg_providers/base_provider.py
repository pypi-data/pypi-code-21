
import os
from collections import MutableMapping

import logging_helper
from fdutil.path_tools import expand_path

logging = logging_helper.setup_logging()


class ConfigObject(MutableMapping):

    def __init__(self,
                 config_file=None,
                 create=False):

        """ Initialise Config class

        :param config_file: Path to config file.
        :param create:      When True file will be created if it doesn't already exist.
        """

        self._config_file = expand_path(config_file)
        self._cfg = None

        # Ensure self.DEFAULT_TEMPLATE is initialised and valid!
        try:
            if not os.path.exists(self.DEFAULT_TEMPLATE):
                raise IOError(u'{cls}.DEFAULT_TEMPLATE: '
                              u'File does not exist'.format(cls=self.__class__.__name__))

        except AttributeError:
            raise NotImplementedError(u'{cls}.DEFAULT_TEMPLATE: Not set!'.format(cls=self.__class__.__name__))

        self._load_config(create=create)

    def _load_config(self,
                     create):

        """ Load config file

        :param create: When True file will be created if it doesn't already exist.
        """

        raise NotImplementedError(u'{cls}.{method}'.format(cls=self.__class__.__name__,
                                                           method=self._load_config.__name__))

    def save(self):

        """ Update config file (Save) """

        raise NotImplementedError(u'{cls}.{method}'.format(cls=self.__class__.__name__,
                                                           method=self.save.__name__))

    def find(self,
             key,
             filters):

        """ Get a filtered list of config items

        :param key:     The config item to run the search on.
                        NOTE: If key is none the search will be run on the highest config level.
        :param filters: List of filter tuples.
                        Tuple format: (Search Key, Search Value, Condition)
                        First should not have a condition
                        i.e [("A", 123), ("A", 789, u'AND')]
                        NOTE: if filters is None the entire key value will be returned.
        :return: dict containing the subset of matching items
        """

        raise NotImplementedError(u'{cls}.{method}'.format(cls=self.__class__.__name__,
                                                           method=self.find.__name__))

    @property
    def cfg(self):

        """ Return the entire contents of the config file

        :return: dict
        """

        raise NotImplementedError(u'{cls}.{method}'.format(cls=self.__class__.__name__,
                                                           method=self.find.__name__))

    @cfg.setter
    def cfg(self, value):

        """ Return the entire contents of the config file

        :return: dict
        """

        raise NotImplementedError(u'{cls}.{method}'.format(cls=self.__class__.__name__,
                                                           method=self.find.__name__))

    def __getitem__(self, item):

        """ Get a specific config item """

        raise NotImplementedError(u'{cls}.{method}'.format(cls=self.__class__.__name__,
                                                           method=self.get_item.__name__))

    def __setitem__(self, key, value):

        """ Set a specific config item """

        raise NotImplementedError(u'{cls}.{method}'.format(cls=self.__class__.__name__,
                                                           method=self.set_item.__name__))

    def __delitem__(self, key):

        """ Delete a specific config item """

        raise NotImplementedError(u'{cls}.{method}'.format(cls=self.__class__.__name__,
                                                           method=self.set_item.__name__))

    def __iter__(self):

        """ Iterate over config items """

        raise NotImplementedError(u'{cls}.{method}'.format(cls=self.__class__.__name__,
                                                           method=self.set_item.__name__))

    def __len__(self):

        """ Get number of config items """

        raise NotImplementedError(u'{cls}.{method}'.format(cls=self.__class__.__name__,
                                                           method=self.set_item.__name__))

    def __str__(self):
        return str(self.cfg)

    def __repr__(self):
        return u'{cls}({dict})'.format(cls=self.__class__, dict=self.__dict__)

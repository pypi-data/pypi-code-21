
import logging_helper
from collections import MutableMapping

logging = logging_helper.setup_logging()


class CfgItem(MutableMapping):

    def __init__(self,
                 cfg_fn,
                 cfg_root,
                 key,
                 **parameters):

        """
        :param cfg_fn:      Function that retrieves the config object
                            for this item
        :param cfg_root:    Root config key to use for this config.
        :param key:         key name for the object from parameters 
        :param parameters:  attributes of the item
        """

        self._cfg = cfg_fn()
        self._cfg_root = cfg_root
        self._key_attr = key
        self._parameters = self._extract_parameters(parameters)

    @property
    def parameters(self):
        return self._parameters

    def _extract_parameters(self,
                            parameters):

        """
        Takes a dict of key value pairs and turns them into instance attributes

        :param dict parameters:

        :return: returns the passed parameters dict 
        """

        # Set each parameter as an attribute
        for key, value in iter(parameters.items()):
            setattr(self, key, value)

        return parameters

    def save_changes(self):

        updated_item = self.__dict__.copy()

        # Remove key parameter
        if self._key_attr in updated_item:
            del updated_item[self._key_attr]

        # remove any hidden parameters
        for k in [key for key in updated_item.keys()
                  if str(key).startswith(u'_')]:
            del updated_item[k]

        key = u'{c}.{d}'.format(c=self._cfg_root,
                                d=getattr(self, self._key_attr))
        self._cfg[key] = updated_item

    def __str__(self):
        return str(unicode(self))

    def __unicode__(self):
        return u'\n'.join(u'{key}: {value}'.format(key=key, value=value)
                          for key, value in iter(self.parameters.items()))

    def __getitem__(self, item):
        return self._parameters[item]

    def __setitem__(self, item, value):
        self._parameters[item] = value
        setattr(self, item, value)

    def __delitem__(self, item):
        del self._parameters[item]
        delattr(self, item)

    def __iter__(self):
        return iter(self._parameters)

    def __len__(self):
        return len(self._parameters)

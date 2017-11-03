
from copy import deepcopy

import logging_helper
from .cfg_item import CfgItem

logging = logging_helper.setup_logging()


class CfgItems(object):

    def __init__(self,
                 cfg_fn,
                 cfg_root,
                 key,
                 has_active=False,
                 item_class=CfgItem):

        """
        
        :param cfg_fn:      Function that retrieves the config object for this item.
        :param cfg_root:    Root config key to use for this config.
        :param key:         key name for the object from parameters.
        :param has_active:  False if no active parameter, The Constant.active value if it does.
        """

        self._cfg_fn = cfg_fn
        self._cfg_root = cfg_root
        self._key_attr = key
        self._has_active = has_active
        self._item_class = item_class

    @property
    def raw_items(self):

        cfg = self._cfg_fn()
        items = cfg[self._cfg_root]
        logging.debug(u'Raw Items: {e}'.format(e=items))

        # Return a copy so that modifications of the retrieved do not get saved in config unless explicitly requested!
        return deepcopy(items)

    def __iter__(self):
        return iter(self.get_items())

    def get_items(self,
                  active_only=False):

        items = []

        for item_name, item_config in iter(self.raw_items.items()):

            if active_only and self._has_active and not item_config[self._has_active]:
                # Item not active and we want active items only
                continue

            item_config[self._key_attr] = item_name

            items.append(self._item_class(cfg_fn=self._cfg_fn,
                                          cfg_root=self._cfg_root,
                                          key=self._key_attr,
                                          **item_config))

        return items

    def get_item(self,
                 item,
                 active_only=False,
                 suppress_refetch=False):

        # Check whether we have been passed the Site object
        if isinstance(item, self._item_class):
            if suppress_refetch:
                return item

            # Set site to path ready for re-fetch
            item = item[self._key_attr]

        for i in self.get_items(active_only=active_only):
            if i[self._key_attr] == item:
                return i

            # Check all additional attributes for site reference
            for attribute in i.parameters.keys():
                if i[attribute] == item:
                    return i

        raise LookupError(u'Unable to find item: {item}'.format(item=item))

    def get_active_items(self):
        return self.get_items(active_only=True)

    def get_active_item(self,
                        **kwargs):
        return self.get_item(active_only=True,
                             **kwargs)

    def add(self,
            key_attr,
            config):

        # Remove key parameter
        if key_attr in config:
            del config[key_attr]

        cfg = self._cfg_fn()
        key = u'{c}.{i}'.format(c=self._cfg_root,
                                i=key_attr)

        cfg[key] = config

    def delete(self,
               key_attr):

        cfg = self._cfg_fn()
        key = u'{k}.{d}'.format(k=self._cfg_root,
                                d=key_attr)

        a = cfg[self._cfg_root]
        del cfg[key]

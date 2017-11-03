
import os
import json

import logging_helper
from fdutil.dict_tools import filter_dict
from fdutil.parse_json import write_json_to_file
from fdutil.path_tools import ensure_path_exists, pop_path
from configurationutil.cfg_providers.base_provider import ConfigObject

logging = logging_helper.setup_logging()

TEMPLATE = u'json_provider_default.json'


class JSONConfig(ConfigObject):

    DEFAULT_TEMPLATE = os.path.join(pop_path(__file__), TEMPLATE)

    def __init__(self,
                 *args,
                 **kwargs):

        """ Initialise JSON Config class """

        super(JSONConfig, self).__init__(*args, **kwargs)

    def _load_config(self,
                     create):

        """ Load config file

        :param create: When True file will be created if it doesn't already exist.
        """

        logging.debug(self._config_file)

        # If file doesn't exist create it
        if not os.path.exists(self._config_file) and create:
            pth = self._config_file.split(os.sep)
            fn, ext = pth.pop().split(u'.')

            pth = os.sep.join(pth)

            ensure_path_exists(pth)

            # Load the template
            template = json.load(open(self.DEFAULT_TEMPLATE))

            # Create the file
            write_json_to_file(content=template,
                               output_dir=pth,
                               filename=fn,
                               file_ext=ext)

        self._cfg = json.load(open(self._config_file))

    def save(self):

        """ Update config file """

        logging.debug(u'Updating config file: {f}'.format(f=self._config_file))
        logging.debug(u'Value: {f}'.format(f=self._cfg))

        path, fn = os.path.split(self._config_file)
        fn, ext = fn.split(u'.')

        write_json_to_file(content=self._cfg,
                           output_dir=path,
                           filename=fn,
                           file_ext=ext)

    def find(self,
             key=None,
             filters=None):

        """ Get a filtered list of config items

        NOTE: Find for JSON is limited to what fdutil.dict_tools.filter_dict is capable of.

        :param key:     The config item to run the search on.
                        NOTE: If key is none the search will be run on the highest config level.
        :param filters: List of filter tuples.
                        Tuple format: (Search Key, Search Value, Condition)
                        First should not have a condition
                        i.e [("A", 123), ("A", 789, u'AND')]
                        NOTE: if filters is None the entire key value will be returned.
        :return: dict containing the subset of matching items
        """

        if key is None:
            # If no key speified set value to entire config object
            value = self._cfg

        else:
            # We have a key so find its value
            items = self.__split_key(key)
            value, _, _ = self.__retrieve_item(self._cfg, items)

            # Need to ensure we have a valid key to search
            if type(value) != dict:
                raise KeyError(u'The value for the provided key is not an object')

        # If filters is none return act like the getter otherwise return the filtered dict
        return value if filters is None else filter_dict(src_dict=value,
                                                         filters=filters)

    @property
    def cfg(self):
        return self._cfg

    @cfg.setter
    def cfg(self, value):
        self._cfg = value

    def __getitem__(self, key):
        items = self.__split_key(key)
        value, _, _ = self.__retrieve_item(self._cfg, items)

        return value

    def __setitem__(self, key, value):
        items = self.__split_key(key)
        self.__add_node(self._cfg, items, value)

    def __delitem__(self, key):
        items = self.__split_key(key)
        _, item_obj, item_key = self.__retrieve_item(self._cfg, items)

        del item_obj[item_key]

    def __iter__(self):
        return iter(self._cfg)

    def __len__(self):
        return len(self._cfg)

    @staticmethod
    def __split_key(key):

        """ Break the requested key into a list of items

        :param key: The config key to be validated
        :return:    List of items to traverse for the requested config value.
        """

        return key.split(u'.')

    def __retrieve_item(self,
                        obj,
                        items):

        """ Traverse the object following the item list to get value for a key

        :param obj:     The object to load the item from
        :param items:   List of items to traverse to get to the requested value
        :return:        item value - The stored config value for the item object
                        item object - The parent object of the value so the value can be updated
        """

        current_item_key = items[0]
        items = items[1:]

        if len(items) == 0:
            return obj[current_item_key], obj, current_item_key

        elif current_item_key in obj and type(obj.get(current_item_key)) == dict:
            # There are still sub keys to search
            # The key exists in the object
            # The keys value is an object
            return self.__retrieve_item(obj[current_item_key], items)

        else:
            items[0] = u'{c}.{i}'.format(c=current_item_key, i=items[0])
            return self.__retrieve_item(obj, items)

    def __add_node(self,
                   obj,
                   items,
                   value):

        """ Add the new node in the item list to the object and set the value

        :param obj:     The object to load the item from
        :param items:   List of items to traverse to get to the position for the new node
        :param value:   The value to set the new node to
        """

        # Get the current item key to find
        current_item_key = items[0]
        items = items[1:]

        if len(items) == 0:
            obj[current_item_key] = value

        elif current_item_key in obj and type(obj.get(current_item_key)) == dict:
            # There are still sub keys to search
            # The key exists in the object
            # The keys value is an object
            self.__add_node(obj[current_item_key], items, value)

        else:
            items[0] = u'{c}.{i}'.format(c=current_item_key, i=items[0])
            self.__add_node(obj, items, value)

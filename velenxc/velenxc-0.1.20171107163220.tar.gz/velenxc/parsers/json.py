
import abc
import logging
from itertools import chain

import jsonpath


class JSONParser(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def parse(self, data, json_paths, **kwargs):
        raise NotImplementedError("Please implement the method of `JSONParser`")


class JSONPathParser(JSONParser):
    """ 使用python的jsonpath第三方库解析json数据 """

    def parse(self, data, json_paths, **kwargs):
        parse_type = kwargs.get('parse_type', 'default')

        parse_values = []
        not_match_path = []

        for json_path in json_paths:
            try:
                value = jsonpath.jsonpath(data, json_path, debug=0)
            except IndexError:
                parse_values = [None]
                logging.warning("path:%s IndexError", json_path)
                break
            if value is False:
                parse_values = [None]
                not_match_path.append(json_path)
                logging.warning("No match path:%s", not_match_path)
                break

            if parse_type == 'zip':
                parse_values.append(value)
                continue

            if isinstance(value, list) and len(value) > 0:
                parse_values = list(chain(*(parse_values, value)))

        return {
            'parse_values': parse_values,
            'not_match_path': not_match_path
        }

import json
from json import JSONDecodeError


class Response:
    def __init__(self, data=None):
        """
        Defines a Response object
        :param data: a string containing xml data
        """
        from evosnap import TransactionRequestException
        if data:
            if isinstance(data,str):
                try:
                    self._json = json.loads(data)
                except JSONDecodeError:
                    raise TransactionRequestException(data)
            elif isinstance(data, dict):
                self._json = data
            else:
                raise TypeError('Data must be a dictionary or string')
        else:
            self._json = {}

    def __getattr__(self, item):
        """
        Search unidentified attributes inside the structure inside the _json attribute.
        :param item: the name of the requested attribute
        :return: the content of the first attribute named item in the structure
        """
        try:
            node = item.split('__')
            element = self._json
            for n in node[:-1]:
                element = element.get(n, {})
            return element.get(node[-1])
        except AttributeError:
            raise AttributeError('{} not found in response.'.format(item))

    def to_json_string(self):
        """
        Turns the data contained by this object into a json string.
        :return: a json string with the data contained by this object.
        """
        return json.dumps(self._json)

    def to_pretty_json(self):
        """
        Turns the data contained by this object into a json string.
        :return: a json string with the data contained by this object.
        """
        return json.dumps(self._json, indent=4, sort_keys=True)

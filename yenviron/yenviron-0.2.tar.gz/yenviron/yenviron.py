import yaml

from . import exceptions


class Yenviron(object):

    def __init__(self, d):
        if not isinstance(d, dict):
            raise exceptions.YenvironError('Yenviron requires a dictionary')
        self.d = d

    def __getitem__(self, key):
        try:
            return self.d.__getitem__(key)
        except KeyError:
            self.__missing__(key)

    def __missing__(self, key):
        raise exceptions.YenvironKeyError('Key {} does not exist'.format(key))

    def __iter__(self):
        return self.d.__iter__()

    def __contains__(self, key):
        return self.d.__contains__(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except exceptions.YenvironKeyError:
            return default

    def follow(self, name):
        return self[self[name]]


def yenviron_parse(stream):
    return Yenviron(yaml.load(stream))


def yenviron_read(file):
    with open(file, 'r') as f:
        return yenviron_parse(f)

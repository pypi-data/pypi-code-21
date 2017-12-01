import yaml


class Yenviron(object):

    def __init__(self, d):
        self.d = d

    def db(self, name):
        return self['DATABASES'][name]

    def cache(self, name):
        return self['CACHES'][name]

    def follow(self, name):
        return self[self[name]]

    def __contains__(self, item):
        return self.d.__contains__(item)

    def __getitem__(self, item):
        return self.d.__getitem__(item)


def yenviron_parse(stream):
    return Yenviron(yaml.load(stream))


def yenviron_read(file):
    return yenviron_parse(open(file, 'r'))

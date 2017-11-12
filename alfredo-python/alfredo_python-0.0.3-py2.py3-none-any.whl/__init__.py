import os
import sys

import ruamel.yaml as yaml

from alfredo import descriptions
from alfredo.resource import HttpPropertyResource

__version__ = '0.0.3'


def represent_unicode(self, data):
    return self.represent_str(data.encode('utf-8'))


if sys.version_info < (3,):
    yaml.representer.Representer.add_representer(unicode, represent_unicode)


def ruote(token=None):
    ruote_root = os.getenv('RUOTE_ROOT', 'https://apibeta.rstor.io')
    root = HttpPropertyResource(None, ruote_root, descriptions.ruote)
    if token is not None:
        root.headers = dict(Authorization="Token %s" % token)
    return root


def virgo():
    virgo_root = os.getenv('VIRGO_ROOT', 'http://virgo.teamjamon.com')
    return HttpPropertyResource(None, virgo_root, descriptions.virgo)

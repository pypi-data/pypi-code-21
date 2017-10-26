'''
'''
import os.path

__title__ = 'olypy'
__author__ = 'Greg Lindahl and others'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2016-2017 Greg Lindahl and others'


def get_mapgen_lib():
    head, tail = os.path.split(__file__)
    return os.path.join(head, 'mapgen-lib')


def get_template_lib():
    head, tail = os.path.split(__file__)
    return os.path.join(head, 'template-lib')

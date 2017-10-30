class Filters(object):
    FILTERS = {}


def register_filter(name):
    def filter_decorator(func):
        Filters.FILTERS[name] = func
        return func
    return filter_decorator


def get_filter_by_name(name):
    return Filters.FILTERS[name]


def get_all_filters():
    return Filters.FILTERS.items()

from .cssmin import *
from .sass import *
from .clojure import *

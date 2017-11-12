#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import collections
import sys

import six


class Traverser(object):
    handlers = dict()

    def __init__(self, obj, consumer):
        self.queue = collections.deque()
        self.queue.append(obj)
        self.consumer = consumer

    def traverse(self):
        kls = self.__class__
        while self.queue:
            obj = self.queue.popleft()
            for typ in obj.__class__.mro():
                if typ in self.handlers:
                    kls.handlers[typ](self, obj)
                    break


def register_handler(*types):
    def decorator(func):
        for typ in types:
            Traverser.handlers[typ] = func
        return func
    return decorator


@register_handler(int, float)
def handle_primatives(traverser, obj):
    s = '<{}:{}>'.format(obj.__class__.__name__, obj)
    traverser.consumer(s)


@register_handler(*six.string_types)
def handle_primatives(traverser, obj):
    if isinstance(obj, six.binary_type) and sys.version_info.major == 2:
        obj = obj.decode()
    s = '<str:{}>'.format(obj)
    traverser.consumer(s)


@register_handler(set)
def handle_set(traverser, obj):
    traverser.consumer('<set>')
    items = list(obj)
    items.sort()
    for item in items:
        traverser.queue.append(item)


@register_handler(list)
def handle_list(traverser, obj):
    traverser.consumer('<list>')
    for item in obj:
        traverser.queue.append(item)


@register_handler(dict)
def handle_dict(traverser, obj):
    traverser.consumer('<dict>')
    keys = list(obj)
    keys.sort()
    for k in keys:
        traverser.queue.append(k)
        traverser.queue.append(obj[k])


# the last resort
@register_handler(object)
def handle_object(traverser, _):
    traverser.consumer('<object>')

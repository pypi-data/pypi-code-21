# coding=utf8
from __future__ import unicode_literals, absolute_import

import importlib

from django.apps import apps


class HooksManager(object):
    def __init__(self, hooks, allow_empty=False):
        self._hooks = {}
        self._model_names = []
        if allow_empty:
            self._model_names.append(('', '---'))
        for hook_name, model_description in hooks.items():
            try:
                model = apps.get_model(model_description['model'])
            except (ValueError, LookupError):
                module, klass = model_description['model'].rsplit('.', 1)
                i = importlib.import_module(module)
                model = getattr(i, klass)
            self._hooks[hook_name] = {
                'model': model,
                'args': model_description.get('args', ()),
                'kwargs': model_description.get('kwargs', {}),
                'description': model_description['description'],
            }
            self._model_names.append((hook_name, model_description['description']))

    def create_object(self, hook_name, item):
        try:
            return self._hooks[hook_name]['model'].create_from_item(
                item, *self._hooks[hook_name]['args'],
                **self._hooks[hook_name]['kwargs']
            )
        except KeyError:
            raise RuntimeError('No hook model with label "{}"'.format(hook_name))

    def get_object(self, hook_name, item):
        try:
            return self._hooks[hook_name]['model'].get_by_item(item)
        except KeyError:
            raise RuntimeError('No hook model with label "{}"'.format(hook_name))

    def get_model_choices(self):
        return self._model_names

    def get_description(self, hook_name):
        return self._hooks.get(hook_name, {}).get('description', '-')

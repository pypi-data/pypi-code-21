#!/usr/bin/env python
# -*- coding: utf-8 -*-


import traceback


def extract_name_category(string):
    split = string.split('__')
    if len(split) == 2:
        return split[0], split[1]
    if len(split) < 2:
        return string, ''
    if len(split) > 2:
        result = split[0:1]
        result.append('__'.join(split[1:]))
        return result[0], result[1]


def case(func):
    name, category = extract_name_category(func.__name__)
    print("name: {}, category: {}".format(name, category))

    def wrapper(self, *args, **kwargs):
        self._log('------ [{}/{}] Starting...'.format(name, category))
        _case = self.add_test(name, category, False, False)
        _case.start()
        try:
            details = func(self)
            if not details:
                details = dict()
            success = True
        except Exception as exc:
            self._log('------ [{}/{}] Test failure or exception: {}'.format(name, category, exc))
            success = False
            details = {'error': '{}'.format(exc), 'stack': traceback.format_exc()}
        _case.end(success, details)
        _case.set_extra_data(details)
        self._log('------ [{}/{}] Ended: {}'.format(name, category, _case.status))
        return _case
    setattr(wrapper, 'is_case', True)
    setattr(wrapper, 'name', name)
    setattr(wrapper, 'category', category)
    setattr(wrapper, 'function_name', func.__name__)
    return wrapper

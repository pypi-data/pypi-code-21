import copy
import os
import re

from . import exceptions
import datamorph.filters


class Template(object):

    def __init__(self, template):
        self.template = template

    def __iter__(self):
        while True:
            start = None
            in_string = False

            for i, s in enumerate(self.template):
                escaped = False

                if i > 0 and self.template[i - 1] == '\\':
                    escaped = True

                if s == '\'' and not escaped:
                    in_string = not in_string
                elif s == '{' and not (escaped or in_string):
                    start = i
                elif s == '}' and not (escaped or in_string or start is None):
                    yield self.template[start + 1: i]
                    break
            else:
                raise StopIteration()

    def replace(self, field, value):
        self.template = self.template.replace('{{{}}}'.format(field), value)
        return self.template

    def __str__(self):
        return '<Template "{}">'.format(self.template)


def morph(schema, data, strict=False):
    """Morph data.

    :param schema: result JSON schema
    :type schema: dict
    :param data: JSON data
    :type data: dict
    :returns: result data
    :rtype: dict
    """
    result = {}

    for key, paths in schema.items():
        if isinstance(paths, dict):
            if key.startswith('root:'):
                data = morph(paths, extract(data, key.split(':')[1], strict))

                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    result.update(data)
                    continue

            result[key] = morph(paths, data)
            continue

        if isinstance(data, list):
            return morph_many(schema, data)

        if isinstance(paths, str):
            paths = [paths]

        for path in paths:
            if '{' in path:
                value = fill(path, data)
            else:
                value = extract(data, path)

            if value:
                result[key] = value
                break

    return result


def morph_many(schema, data, strict=False):
    """Morph data list.

    :param schema: result JSON schema
    :type schema: dict
    :param data: JSON data
    :type data: list
    :param strict: strict mode
    :type strict: `bool`
    :returns: result data
    :rtype: list
    """
    results = []

    for item in data:
        results.append(morph(copy.copy(schema), item, strict))

    return results


def extract(data, path, default=None, strict=False):
    """Extract value by path.

    :param data: JSON data
    :type data: `dict` or `list`
    :param path: path for search value
    :type path: `str`
    :param default: default value
    :type default: `any`
    :param strict: strict mode
    :type strict: `bool`
    :return: found value or None
    :rtype: type
    """
    paths = path.split('.')

    for key in paths:
        if isinstance(data, list):
            if key.isdigit():
                try:
                    data = data[int(key)]
                    continue
                except IndexError:
                    if strict:
                        raise exceptions.PathError(path, key, range(len(data)))

                    return default

            results = []

            for item in data:
                result = extract(item, '.'.join(paths))

                if isinstance(result, list):
                    results.extend(result)
                elif result:
                    results.append(result)

            return results

        try:
            data = data[key]
        except (TypeError, KeyError):
            if strict:
                raise exceptions.PathError(path, key, data.keys())

            return default

        paths = paths[1:]

    return data


def fill(template, data, many=False, strict=False):
    """Fill string template like a str.format() using nested access to data.

    :param template: template for filling
    :type template: str
    :param data: data for filling
    :type data: list or dict
    :param many (optional): If True, lists uncovers
    :type many: bool
    :param strict: strict mode
    :type strict: `bool`
    :returns: filled string or lists of strings, if `many=True`
    :rtype: str
    """
    def prepare(template, field, filters, value):
        for name, args in filters:
            value = getattr(datamorph.filters, name)(value, *args)

        value = str(value).replace('{', r'\{').replace('}', r'\}')

        return template.replace(field, value)

    template = Template(template)

    for field in template:
        path, *filters = field.split('|', 1)

        if filters:
            filters = datamorph.filters.parse_filters(filters[0])

        value = extract(data, path, '', strict)

        if isinstance(value, list) and many:
            results = []

            for item in value:
                _template = Template(template.template)
                item = prepare(_template, field, filters, item)
                results.extend(fill(item, data, many=True))

            return results

        prepare(template, field, filters, value)

    if many:
        return [template.template]

    return template.template.replace(r'\{', '{').replace(r'\}', '}')

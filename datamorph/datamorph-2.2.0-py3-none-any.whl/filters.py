# coding=utf-8

import random as _random
import re


RE_FILTER = re.compile(r'(\w+)(\((.*)\))?')


def parse_filters(filters_string):
    filters = []
    data = []

    start = 0
    in_string = False

    for i, symbol in enumerate(filters_string):
        if symbol == '\'' and filters_string[i-1] != '\\':
            in_string = not in_string
        elif symbol == '|' and not in_string:
            filters.append(filters_string[start: i])
            start = i + 1

    filters.append(filters_string[start:])

    for filter_ in filters:
        match = RE_FILTER.search(filter_)
        name = match.group(1).strip()

        args_string, args = match.group(3), []

        if args_string:
            start = 0
            in_string = False

            for i, symbol in enumerate(args_string):
                if symbol == '\'' and args_string[i - 1] != '\\':
                    in_string = not in_string
                elif symbol == ',' and not in_string:
                    arg = args_string[start: i].strip()
                    args.append(arg.replace('\\\'', '\'').replace('\'', ''))
                    start = i + 1

            arg = args_string[start:].strip()
            args.append(arg.replace('\\\'', '\'').replace('\'', ''))

        if name in globals():
            data.append((name, args))

    return data


def strip(value, character=' '):
    return value.strip(character)


def regex(value, pattern, index=0):
    try:
        return re.findall(pattern, value)[int(index)]
    except IndexError:
        return ''


def default(value, default_value):
    return value or default_value


def replace(value, pattern, replacement):
    return re.sub(pattern, replacement, value)


def random(value):
    try:
        return _random.choice(value)
    except (IndexError, KeyError, TypeError):
        return ''

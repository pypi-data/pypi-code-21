import re
import os

from .tagger import FIELDS


def parse_filename(fname, pattern):
    basename, _ = os.path.splitext(os.path.abspath(fname))
    regexp = construct_regexp(pattern)
    parsed = re.search(regexp, basename).groupdict()
    for key in parsed:
        parsed[key] = parsed[key].replace('_', ' ')
    return parsed


def construct_regexp(pattern):
    fields = set(get_fields(pattern))
    regexp = pattern.replace('(', r'\(').replace(')', r'\)')
    regexp = regexp.replace('<__any__>', '[^/]+')
    number_fields = {'bpm', 'year', 'tracknumber'}
    complex_fields = number_fields | {'key'}
    simple_fields = list(fields - complex_fields)
    regexp = re.sub(r'<({})>'.format('|'.join(simple_fields)),
                    r'(?P<\1>[^/]+)',
                    regexp)
    for field in number_fields:
        if field in fields:
            regexp = re.sub(r'<{}>'.format(field),
                            r'(?P<{}>\d+)'.format(field),
                            regexp)

    if 'key' in fields:
        regexp = re.sub(r'<key>', r'(?P<key>\d+[ABab])', regexp)
    return regexp + '$'


def get_fields(pattern):
    fields = {(field.split('.')[0],
               field.split('.')[1] if len(field.split('.')) == 2 else None)
              for field in re.findall(r'<(.*?)>', pattern)}
    return {field: formatter
            for field, formatter in fields
            if field in FIELDS}

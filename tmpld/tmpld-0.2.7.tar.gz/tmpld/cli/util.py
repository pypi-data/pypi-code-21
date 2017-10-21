"""
tmpld.cli.util
~~~~~~~~~~~~~~

Cement CLI utility methods and classes.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import unicodedata
import re
import os


def parse_bool(string):
    if string.lower() in ('yes', 'y', 'true', '1'):
        return True
    elif string.lower() in ('no', 'n', 'false', '0'):
        return False


def slugify(string):
    string = unicodedata.normalize('NFKD', string)
    string = re.sub(r'[^\w\s_-]', '', string).strip().lower()
    string = re.sub(r'\s+', '-', string)
    return re.sub(r'^-|-$', '', string)


def slugify_path(path):
    filename = os.path.basename(path)
    basename = filename.split('.', 1)[0]
    return slugify(basename)


def get_file_extension(path):
    return os.path.basename(path).rsplit('.', 1)[-1]


def get_template_dirs(templates=None):
    templates = templates or []
    return list(set(
        [os.path.dirname(os.path.abspath(t.file)) for t in templates]))

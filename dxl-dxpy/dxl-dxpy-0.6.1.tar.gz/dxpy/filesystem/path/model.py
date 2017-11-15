"""
Abstract of path object.
Features:
    An unified model for path, pathlib.Path, fs.path, and url encoded path.
"""

import fs.path as fp
from fs.path import normpath
from fs import opener
from urllib.parse import quote_plus as qut
from urllib.parse import unquote_plus as uqut
import pathlib
from ruamel.yaml import YAML


from ..exceptions import NonePathError, ConflictUrlSpecError


class UrlSpec:
    def __init__(self, protocol=None, username=None, password=None, resource=None, params=None):
        self.protocol = protocol
        self.username = username
        self.password = password
        self.resource = resource
        self.params = params

    def __eq__(self, url_spec):
        compares = [self.protocol == url_spec.protocol,
                    self.username == url_spec.username,
                    self.password == url_spec.password,
                    self.resource == url_spec.resource]
        return all(compares)

    @classmethod
    def parse(cls, s):
        p = opener.parse.parse_fs_url(s)
        return cls(p.protocol, p.username, p.password, p.resource, p.params)

    def serilization(self, format='JSON'):
        def to_json_dct():
            return {'protocol': self.protocol,
                    'username': self.username,
                    'password': self.password,
                    'resource': self.resource,
                    'params': self.params}
        if format.upper() == 'JSON':
            pass
        return None


QUOTED_SLASH = qut('/')
DOUBLE_QUOTED_SLASH = qut(qut('/'))


def is_quoted_url(s):
    return QUOTED_SLASH in s


def is_double_quoted_url(s):
    return DOUBLE_QUOTED_SLASH in s


def url_quote_path(path):
    return qut(path)


def url_unquote_path(url):
    return uqut(url)


def url_double_quoted_path(path):
    return qut(qut(path))


def url_double_unquoted_path(path):
    return uqut(uqut(path))


def unified_path_to_str(path):
    if path is None:
        raise NotValidPathError
    if isinstance(path, str):
        if is_quoted_url(path):
            path = url_unquote_path(path)
        return normpath(path)
    if isinstance(path, Path):
        return unified_path_to_str(str(path.path))
    if isinstance(path, pathlib.Path):
        return unified_path_to_str(str(path))


class Path:
    """ Unified path for posix/windows/url/url_quoted paths.
    This class is an 'abstract' path object, which means it only normalize its representation for different platform,
    and provide functionalities of pure path calculations, without any relation to the true file system.
    Thus this class does **NOT** provide methods like `exists()` or `is_dir()`, please refer `dxpy.file_syste.file.File` for these functions.
    """
    yaml_tag = '!path'

    def __init__(self, path, url_spec=None):
        """
        """
        self.path = unified_path_to_str(path)
        self.url_spec = url_spec

    @classmethod
    def copy(cls, path, url_spec=None):
        if isinstance(path, Path):
            raw_path = fp.normpath(str(path.path))
            if url_spec is not None and not path.url_spec == url_spec:
                raise ConflictUrlSpecError
            new_url_spec = UrlSpec(url_spec.protocol, url_spec.username,
                                   url_spec.password, url_spec.resource,
                                   url_spec.params)
            return cls(raw_path, new_url_spec)
        if isinstance(path, pathlib.Path):
            return cls(str(path.absolute()), None)

    def __str__(self):
        if self.url_spec is None:
            return self.path
        else:
            fmt = "__str__ for Path with not None url_spec is not Implemented yet, path: {0}, url_spec: {1}."
            raise TypeError(fmt.format(self.path, self.url_spec))

    def __truediv__(self, name):
        return Path(fp.combine(self.abs, name), self.url_spec)

    def __add__(self, suffix):
        return Path(self.abs + suffix)

    def check_exists(self, fs):
        return fs.exists(self.abs)

    @property
    def abs(self):
        if fp.isabs(self.path):
            return self.path
        else:
            from fs.osfs import OSFS
            with OSFS('.') as fs:
                return fs.getsyspath(self.path)

    @property
    def rel(self):
        return fp.relpath(self.path)

    @property
    def isabs(self):
        return fp.isabs(self.path)

    @property
    def isrel(self):
        return not fp.isabs(self.path)

    @property
    def parts(self):
        result = fp.iteratepath(self.path)
        if fp.isabs(self.path) and not result[0] == '/':
            result = ['/'] + result
        return tuple(result)

    def rel_parts(self):
        result = fp.iteratepath(self.path)
        if result[0] == '/':
            result = result[1:]
        return result

    @property
    def recurse(self):
        return fp.recursepath(self.path)

    @property
    def father_path(self):
        return Path(fp.dirname(self.path))

    @property
    def father(self):
        return fp.dirname(self.path)

    @property
    def name(self):
        return fp.basename(self.path)

    @property
    def quoted_url(self):
        return qut(qut(self.path))

    @property
    def suffix(self):
        return fp.splitext(self.path)[1]

    def __eq__(self, path):
        return self.path == Path(path).path

    @classmethod
    def to_yaml(cls, representer, obj):
        return representer.represent_scalar(cls.yaml_tag, obj.abs)

    @classmethod
    def from_yaml(cls, constructor, node):
        return Path(constructor.construct_scalar(node))

    def __hash__(self):
        return hash(self.path)


yaml = YAML()
yaml.register_class(Path)

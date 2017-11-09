import os
import yaml

from .stream import StreamMeta


def _cast(name, value):
    """Cast the type of `value` to that of `name`."""
    val_type = type(name).__name__

    if val_type == 'bool':
        return value.lower() in ('1', 't', 'true', 'y', 'yes')
    elif val_type == 'int':
        return int(value)
    return value


def flat_list(paths):
    for path in paths:
        if not os.path.isfile(path):
            return False
        if os.path.getsize(path) > StreamMeta.chunk_size:
            return False
    return True


def as_list(paths):
    if len(paths) == 1:
        path = paths[0]
        if os.path.isdir(path):
            return flat_list(
                map(lambda x: '{}/{}'.format(path, x), os.listdir(path)))
    return flat_list(paths)


def rel_abs(paths):
    """Convert a list of paths to a list of absolute paths."""
    return map(os.path.abspath, paths)


def abs_arc(paths):
    """Strip the common path of a list of absolute paths."""
    path_lists = map(lambda x: x.split('/')[:-1], paths)

    trim = 0
    for path in map(set, zip(*path_lists)):
        if len(path) > 1:
            break
        trim += len(path.pop()) + 1

    return map(lambda x: x[trim:], paths)


class _File(object):
    _style = {
        'width': 76,
        'default_flow_style': False}

    def __init__(self):
        """Initialistion."""
        if not os.path.isfile(self._file):
            if not os.path.isdir(self._path):
                os.makedirs(self._path)
            with open(self._file, 'w') as handle:
                yaml.safe_dump(self._template, handle, **self._style)

        with open(self._file) as handle: 
            self._content = yaml.safe_load(handle)

    def __del__(self):
        self.flush()

    def flush(self):
        """Write the content to disk."""
        with open(self._file, 'w') as handle:
            yaml.safe_dump(self._content, handle, **self._style)


class Config(_File):
    _path = '{}/.config/transfer_client'.format(os.getenv('HOME'))
    _file = '{}/config.yml'.format(_path)
    _template = {
        'defaults': {
            'output_format': 'json',
            'project': '',
            'server': '',
            'ssl_check': True,
            'ca_bundle': ''},
        'projects': {}}
    _err_novar = 'no such variable'
    _err_noproject = 'no such project'
    _err_existingproject = 'project exists'

    def __init__(self):
        """Initialistion."""
        super(Config, self).__init__()

        self._defaults = self._content['defaults']
        self._projects = self._content['projects']

    def set_default(self, name, value):
        """Sat a configuration variable."""
        if name not in self._defaults:
            raise ValueError(self._err_novar)
        if name == 'project' and value not in self._projects:
            raise ValueError(self._err_noproject)
        self._defaults[name] = _cast(self._defaults[name], value)
        self.flush()

        return str(self._defaults[name])

    def get_default(self, name):
        """Retrieve a configuration variable."""
        if name not in self._defaults:
            raise ValueError(self._err_novar)
        return self._defaults[name]

    def defaults(self):
        """Retrieve all configuration variable."""
        return self._defaults

    def add_project(self, name, cert_path, key_path):
        """Add a project."""
        if name in self._projects:
            raise ValueError(self._err_existingproject)
        self._projects[name] = {
            'cert': os.path.abspath(cert_path),
            'key': os.path.abspath(key_path)}
        self.flush()

    def del_project(self, name):
        """Remove a project."""
        if name not in self._projects:
            raise ValueError(self._err_noproject)
        if self._defaults['project'] == name:
            self._defaults['project'] = None
        del self._projects[name]
        self.flush()

    def get_project(self, name):
        """Retrieve project information."""
        if name not in self._projects:
            raise ValueError(self._err_noproject)
        return self._projects[name]

    def projects(self):
        """Retrieve project information for all projects."""
        return self._projects


class Cache(_File):
    _path = '{}/.cache/transfer_client'.format(os.getenv('HOME'))
    _file = '{}/cache.yml'.format(_path)
    _template = {}

    def __init__(self):
        super(Cache, self).__init__()

    def set_entry(self, project_name, data):
        """Set a cache entry."""
        self._content[project_name] = data
        self.flush()

    def get_entry(self, project_name):
        """Retrieve a cache entry."""
        return self._content[project_name]

    def del_entry(self, project_name):
        """Remove a cache entry."""
        del self._content[project_name]
        self.flush()

    def purge(self):
        """Purge the cache."""
        self._content = {}
        self.flush()

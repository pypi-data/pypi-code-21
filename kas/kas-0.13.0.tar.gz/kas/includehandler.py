# kas - setup tool for bitbake based projects
#
# Copyright (c) Siemens AG, 2017
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
    This module implements how includes of configuration files are handled in
    kas.
"""

import os
import collections
import functools
import logging

from . import __file_version__, __compatible_file_version__

__license__ = 'MIT'
__copyright__ = 'Copyright (c) Siemens AG, 2017'


class LoadConfigException(Exception):
    """
        Class for exceptions that appear while loading the configuration file.
    """
    def __init__(self, message, filename):
        super().__init__('{}: {}'.format(message, filename))


def load_config(filename):
    """
        Load the configuration file and test if version is supported.
    """
    (_, ext) = os.path.splitext(filename)
    config = None
    if ext == '.json':
        import json
        with open(filename, 'rb') as fds:
            config = json.load(fds)
    elif ext == '.yml':
        import yaml
        with open(filename, 'rb') as fds:
            config = yaml.safe_load(fds)
    else:
        raise LoadConfigException('Config file extension not recognized',
                                  filename)

    try:
        header = config.get('header', {})
    except AttributeError:
        raise LoadConfigException('Config does not contain a dictionary',
                                  filename)

    if not header:
        raise LoadConfigException('Header missing or empty', filename)

    try:
        version = header.get('version', None)
    except AttributeError:
        raise LoadConfigException('Header is not a dictionary', filename)

    if not version:
        raise LoadConfigException('Version missing or empty', filename)

    try:
        version_value = int(version)
    except ValueError:
        # Be compatible: version string '0.10' is equivalent to file version 1
        if isinstance(version, str) and version == '0.10':
            version_value = 1
        else:
            raise LoadConfigException('Unexpected version format', filename)

    if version_value < __compatible_file_version__ or \
       version_value > __file_version__:
        raise LoadConfigException('This version of kas is compatible with '
                                  'version {} to {}, file has version {}'
                                  .format(__compatible_file_version__,
                                          __file_version__, version_value),
                                  filename)

    return config


class IncludeException(Exception):
    """
        Class for exceptions that appear in the include mechanism.
    """
    pass


class IncludeHandler(object):
    """
        Abstract class that defines the interface of an include handler.
    """

    def __init__(self, top_file):
        self.top_file = top_file

    def get_config(self, repos=None):
        """
        Parameters:
          repos -- A dictionary that maps repo name to directory path

        Returns:
          (config, repos)
            config -- A dictionary containing the configuration
            repos -- A list of missing repo names that are needed \
                     to create a complete configuration
        """
        # pylint: disable=no-self-use,unused-argument

        logging.error('get_config is not implemented')
        raise NotImplementedError()


class GlobalIncludes(IncludeHandler):
    """
        Implements a handler where every configuration file should
        contain a dictionary as the base type with and 'includes'
        key containing a list of includes.

        The includes can be specified in two ways, as a string
        containg the relative path from the current file or as a
        dictionary. The dictionary should have a 'file' key, containing
        the relative path to the include file and optionally a 'repo'
        key, containing the key of the repository. If the 'repo' key is
        missing the value of the 'file' key is threated the same as if
        just a string was defined, meaning the path is relative to the
        current config file otherwise its relative to the repository path.

        The includes are read and merged depth first from top to buttom.
    """

    def get_config(self, repos=None):
        repos = repos or {}

        def _internal_include_handler(filename):
            """
            Recursively load include files and find missing repos.

            Includes are done in the following way:

            topfile.yml:
            -------
            header:
              includes:
                - include1.yml
                - file: include2.yml
                - repo: repo1
                  file: include-repo1.yml
                - repo: repo2
                  file: include-repo2.yml
                - include3.yml
            -------

            Includes are merged in in this order:
            ['include1.yml', 'include2.yml', 'include-repo1.yml',
             'include-repo2.yml', 'include-repo2.yml', 'topfile.yml']
            On conflict the latter includes overwrite previous ones and
            the current file overwrites every include. (evaluation depth first
            and from top to buttom)
            """
            missing_repos = []
            configs = []
            current_config = load_config(filename)
            if not isinstance(current_config, collections.Mapping):
                raise IncludeException('Configuration file does not contain a '
                                       'dictionary as base type')
            header = current_config.get('header', {})

            for include in header.get('includes', []):
                if isinstance(include, str):
                    includefile = ''
                    if include.startswith(os.path.pathsep):
                        includefile = include
                    else:
                        includefile = os.path.abspath(
                            os.path.join(
                                os.path.dirname(filename),
                                include))
                    (cfg, rep) = _internal_include_handler(includefile)
                    configs.extend(cfg)
                    missing_repos.extend(rep)
                elif isinstance(include, collections.Mapping):
                    includerepo = include.get('repo', None)
                    if includerepo is not None:
                        includedir = repos.get(includerepo, None)
                    else:
                        raise IncludeException(
                            '"repo" is not specified: {}'
                            .format(include))
                    if includedir is not None:
                        try:
                            includefile = include['file']
                        except KeyError:
                            raise IncludeException(
                                '"file" is not specified: {}'
                                .format(include))
                        (cfg, rep) = _internal_include_handler(
                            os.path.abspath(
                                os.path.join(
                                    includedir,
                                    includefile)))
                        configs.extend(cfg)
                        missing_repos.extend(rep)
                    else:
                        missing_repos.append(includerepo)
            configs.append((filename, current_config))
            return (configs, missing_repos)

        def _internal_dict_merge(dest, upd, recursive_merge=True):
            """
            Merges upd recursively into a copy of dest as OrderedDict

            If recursive_merge=False, will use the classic dict.update,
            or fall back on a manual merge (helpful for non-dict types
            like FunctionWrapper)
            """
            if (not isinstance(dest, collections.Mapping)) \
                    or (not isinstance(upd, collections.Mapping)):
                raise IncludeException('Cannot merge using non-dict')
            dest = collections.OrderedDict(dest)
            updkeys = list(upd.keys())
            if not set(list(dest.keys())) & set(updkeys):
                recursive_merge = False
            if recursive_merge:
                for key in updkeys:
                    val = upd[key]
                    try:
                        dest_subkey = dest.get(key, None)
                    except AttributeError:
                        dest_subkey = None
                    if isinstance(dest_subkey, collections.Mapping) \
                            and isinstance(val, collections.Mapping):
                        ret = _internal_dict_merge(dest_subkey, val)
                        dest[key] = ret
                    else:
                        dest[key] = upd[key]
                return dest
            try:
                for k in upd:
                    dest[k] = upd[k]
            except AttributeError:
                # this mapping is not a dict
                for k in upd:
                    dest[k] = upd[k]
            return dest

        configs, missing_repos = _internal_include_handler(self.top_file)
        config = functools.reduce(_internal_dict_merge,
                                  map(lambda x: x[1], configs))
        return config, missing_repos

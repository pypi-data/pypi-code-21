# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Helpers to retrieve runtime informations
"""
import datetime
import os
import platform
import sys
import threading
from hashlib import sha1
from logging import getLogger

import pkg_resources

from .exceptions import UnsupportedFrameworkVersion, UnsupportedPythonVersion
from .metadata import __version__

LOGGER = getLogger(__name__)


def get_installed_distributions():
    """ Mimic pip.get_installed_distributions using pkg_resources
    """
    return pkg_resources.working_set


def _format_datetime_isoformat(datetime_object):
    """ Take a datetime and return it as isoformat
    """
    return datetime_object.isoformat()


def get_pid_cmdline(pid):
    """ Try to recover the process parent cmdline
    """
    path = "/proc/{}/cmdline".format(pid)
    try:
        with open(path, 'r') as cmdline_file:
            raw_cmdline = cmdline_file.read()

        return raw_cmdline.replace("\x00", " ")
    except Exception:
        LOGGER.warning("Error reading %s path", path)
        return ""


def get_process_cmdline():
    """ Returns the current process cmdline and returns it as a string
    """
    # Retrieve the command used to launch the process
    if hasattr(sys, 'argv') and len(sys.argv) >= 1:
        return " ".join(sys.argv)
    else:
        return get_pid_cmdline(os.getpid())


def get_parent_cmdline():
    """ Returns the parent process cmdline and returns it as a string
    """
    return get_pid_cmdline(os.getppid())


def parse_minor_version(version):
    """ Parse a version and return MAJOR, MINOR as a tuple.

    >>> parse_minor_version('1.9.1')
    (1, 9)
    """
    return tuple(map(int, version.split('.')[:2]))


class RuntimeStorage(object):
    """ Object for storing runtime informations like the current request processed
    """

    def __init__(self):
        self.local = threading.local()

    def store_request(self, request):
        """ Store a request, whatever its kind in a thread-safe way
        """
        self.local.current_request = request
        self.local.__dict__.pop('whitelist_match', None)

    def store_request_default(self, request):
        """ Store a request, whatever its kind in a thread-safe way only if no
        request was stored before
        """
        self.local.__dict__.setdefault('current_request', request)
        self.local.__dict__.pop('whitelist_match', None)

    def clear_request(self):
        """ Clear the stored request in a thread-safe way
        """
        self.local.__dict__.pop('current_request', None)

    def store_current_args(self, binding_accessor):
        """ For daemon only - returns the faked list of arguments """

        args = {}
        for name, value in binding_accessor.items():
            if name.find("#.args[") == 0:
                idx = int(name[7:name.rindex("]")])
                args[idx] = value
            elif name.find("#.cargs[") == 0:
                idx = int(name[8:name.rindex("]")])
                args[idx] = value

        self.local.arguments = [args.get(i) for i in range(0, max(args) + 1)] if args else []

    def get_current_args(self, args=None):
        """ For daemon only - returns the faked list of arguments """
        return getattr(self.local, 'arguments', args)

    def get_current_request(self):
        """ Return current processed request
        """
        return getattr(self.local, 'current_request', None)

    def get_whitelist_match(self, runner_settings):
        """ Return the current whitelisted path or IP, or None if the request
        is not whitelisted.
        """
        # None is a valid value, so let's default to False when not defined.
        whitelist_match = getattr(self.local, 'whitelist_match', False)
        if whitelist_match is not False:
            return whitelist_match
        current_request = self.get_current_request()
        if current_request is None:
            whitelist_match = None
        else:
            whitelist_match = runner_settings.whitelist_match(current_request)
        setattr(self.local, 'whitelist_match', whitelist_match)
        return whitelist_match


runtime = RuntimeStorage()

SUPPORTED_PYTHON_VERSIONS = [(2, 7), (3, 4), (3, 5), (3, 6)]


class RuntimeInfos(object):
    """ Helper to collect and return environement informations about the
    runtime
    """

    def all(self):
        """ Returns aggregated infos from the environment
        """
        resultat = {'various_infos': {}}
        resultat.update(self._agent())
        resultat.update(self._framework())
        resultat.update(self._os())
        resultat.update(self._runtime())
        resultat.update(self._bundle_signature())
        resultat['various_infos'].update(self._time())
        resultat['various_infos'].update(self._dependencies())
        resultat['various_infos'].update(self._process())
        return resultat

    @staticmethod
    def _dependencies():
        """ Returns informations about the installed python dependencies
        """
        dep = [{
            'name': package.project_name,
            'version': package.version
        } for package in get_installed_distributions()]
        return {"dependencies": dep}

    @staticmethod
    def _bundle_signature():
        """ Returns the signature of installed Python dependencies
        """
        pkgvers = sorted((package.project_name, package.version)
                         for package in get_installed_distributions())
        pkgvers = '|'.join('{}-{}'.format(name, version)
                           for name, version in pkgvers)
        sig = sha1(pkgvers.encode()).hexdigest()
        return {'bundle_signature': sig}

    @staticmethod
    def _time():
        """ Returns informations about the current time
        """
        return {'time': _format_datetime_isoformat(datetime.datetime.utcnow())}

    @staticmethod
    def _agent():
        """ Returns informations about the agent
        """
        return {'agent_type': 'python', 'agent_version': __version__}

    @staticmethod
    def _get_package_version(package_name):
        for package in get_installed_distributions():
            if package.project_name == package_name:
                return package.version

    def _framework(self):
        """ Returns informations about the web framework.
        Also check version of Django.
        """
        flask = self._get_package_version('Flask')
        django = self._get_package_version('Django')
        pyramid = self._get_package_version('pyramid')

        if django:
            django_version = parse_minor_version(django)
            # Check for Django version
            if django_version < (1, 6) or django_version >= (1, 12):
                raise UnsupportedFrameworkVersion('django', django)

            return {'framework_type': 'Django', 'framework_version': django}
        elif flask:
            flask_version = parse_minor_version(flask)
            # Check for Flask version
            if flask_version < (0, 10) or flask_version >= (0, 13):
                raise UnsupportedFrameworkVersion('flask', flask)

            return {'framework_type': 'Flask', 'framework_version': flask}
        elif pyramid:
            pyramid_version = parse_minor_version(pyramid)
            if pyramid_version < (1, 6) or pyramid_version >= (1, 10):
                raise UnsupportedFrameworkVersion('pyramid', pyramid)

            return {'framework_type': 'Pyramid', 'framework_version': pyramid}
        else:
            return {'framework_type': None, 'framework_version': None}

    @staticmethod
    def _os():
        """ Returns informations about the os
        """

        # Compute the OS version
        if sys.platform == 'darwin':
            base_os_version = 'Mac OS X {}'.format(platform.mac_ver()[0])
        elif 'linux' in sys.platform:
            base_os_version = '{0[0]} {0[1]}'.format(platform.linux_distribution())
        else:
            base_os_version = ''

        os_version = '{}/{}'.format(base_os_version, '/'.join(os.uname()))
        return {'os_type': '{}-{}'.format(platform.machine(), sys.platform),
                'os_version': os_version,
                'hostname': platform.node()}

    @staticmethod
    def _runtime():
        """ Returns informations about the python runtime
        """

        # Check that the python version is supported
        python_version = tuple(map(int, platform.python_version_tuple()[:2]))
        if python_version not in SUPPORTED_PYTHON_VERSIONS:
            raise UnsupportedPythonVersion(platform.python_version())

        python_build = platform.python_build()
        version = '{} ({}, {})'.format(platform.python_version(), python_build[0],
                                       python_build[1])

        return {'runtime_type': platform.python_implementation(),
                'runtime_version': version}

    @staticmethod
    def _process():
        """ Returns informations about the current process
        """
        return {
            'pid': os.getpid(),
            'ppid': os.getppid(),
            'ppid_cmdline': get_parent_cmdline(),
            'euid': os.geteuid(),
            'egid': os.getegid(),
            'uid': os.getuid(),
            'gid': os.getgid(),
            # sys.argv is not always available
            'name': get_process_cmdline()
        }

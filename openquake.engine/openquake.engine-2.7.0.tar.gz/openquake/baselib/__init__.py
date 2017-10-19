# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2017 GEM Foundation
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import collections
from openquake.baselib.python3compat import configparser
from openquake.baselib.general import git_suffix

# the version is managed by packager.sh with a sed
__version__ = '2.7.0'
__version__ += git_suffix(__file__)


class DotDict(collections.OrderedDict):
    """
    A string-valued dictionary that can be accessed with the "." notation
    """
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)


config = DotDict()  # global configuration
if 'VIRTUAL_ENV' in os.environ or hasattr(sys, 'real_prefix'):
    config.paths = [
        os.path.join(os.environ.get('VIRTUAL_ENV', '~'), 'openquake.cfg')]
else:  # installation from packages, search in /etc
    config.paths = ['/etc/openquake/openquake.cfg']
cfgfile = os.environ.get('OQ_CONFIG_FILE')
if cfgfile:  # has the precedence
    config.paths.insert(0, cfgfile)


def read(*paths, **validators):
    """
    Load the configuration, make each section available in a separate dict.

    The configuration location can specified via an environment variable:
       - OQ_CONFIG_FILE

    In the absence of this environment variable the following paths will be
    used:
       - $VIRTUAL_ENV/openquake.cfg when in a virtualenv
       - /etc/openquake/openquake.cfg outside of a virtualenv

    If those files are missing, the fallback is the source code:
       - openquake/engine/openquake.cfg

    Please note: settings in the site configuration file are overridden
    by settings with the same key names in the OQ_CONFIG_FILE openquake.cfg.
    """
    paths = list(paths) + config.paths
    parser = configparser.SafeConfigParser()
    found = parser.read(os.path.normpath(os.path.expanduser(p)) for p in paths)
    if not found:
        raise IOError('No configuration file found in %s' % str(paths))
    config.clear()
    for section in parser.sections():
        config[section] = sec = DotDict(parser.items(section))
        for k, v in sec.items():
            sec[k] = validators.get(k, lambda x: x)(v)


config.read = read


def boolean(flag):
    """
    Convert string in boolean
    """
    s = flag.lower()
    if s in ('1', 'yes', 'true'):
        return True
    elif s in ('0', 'no', 'false'):
        return False
    raise ValueError('Unknown flag %r' % s)


d = os.path.dirname
config.read(os.path.join(d(d(__file__)), 'engine', 'openquake.cfg'),
            soft_mem_limit=int, hard_mem_limit=int, port=int,
            multi_user=boolean)

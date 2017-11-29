# This file is part of tako
# Copyright (c) 2015-2017 Adam Hartz <hartz@mit.edu> and contributors
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# tako is a fork of xonsh (http://xon.sh)
# xonsh is Copyright (c) 2015-2016 the xonsh developers and is licensed under
# the 2-Clause BSD license.

import os
import re
import pickle
import builtins
import subprocess

from takoshell.completers.tools import get_filter_function

OPTIONS = None
OPTIONS_PATH = None

SCRAPE_RE = re.compile(r'^(?:\s*(?:-\w|--[a-z0-9-]+)[\s,])+', re.M)
INNER_OPTIONS_RE = re.compile(r'-\w|--[a-z0-9-]+')


def complete_from_man(prefix, line, start, end, ctx):
    """
    Completes an option name, based on the contents of the associated man
    page.
    """
    global OPTIONS, OPTIONS_PATH
    if OPTIONS is None:
        datadir = builtins.__tako_env__['TAKO_SETTINGS'].data_dir
        OPTIONS_PATH = os.path.join(datadir, 'man_completions_cache')
        try:
            with open(OPTIONS_PATH, 'rb') as f:
                OPTIONS = pickle.load(f)
        except:
            OPTIONS = {}
    if not prefix.startswith('-'):
        return set()
    cmd = line.split()[0]
    if cmd not in OPTIONS:
        try:
            manpage = subprocess.Popen(
                ["man", cmd], stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL)
            # This is a trick to get rid of reverse line feeds
            text = subprocess.check_output(
                ["col", "-b"], stdin=manpage.stdout)
            text = text.decode('utf-8')
            scraped_text = ' '.join(SCRAPE_RE.findall(text))
            matches = INNER_OPTIONS_RE.findall(scraped_text)
            OPTIONS[cmd] = matches
            with open(OPTIONS_PATH, 'wb') as f:
                pickle.dump(OPTIONS, f)
        except:
            return set()
    return {s for s in OPTIONS[cmd]
            if get_filter_function()(s, prefix)}

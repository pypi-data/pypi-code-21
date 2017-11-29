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

import builtins
from collections import OrderedDict

from takoshell.completers.man import complete_from_man
from takoshell.completers.base import complete_base
from takoshell.completers.path import complete_path
from takoshell.completers.dirs import complete_cd, complete_rmdir
from takoshell.completers.python import (complete_python, complete_import,
                                     complete_python_mode)
from takoshell.completers.commands import complete_skipper
from takoshell.completers.completer import complete_completer

completers = OrderedDict([
    ('python_mode', complete_python_mode),
    ('base', complete_base),
    ('completer', complete_completer),
    ('skip', complete_skipper),
    ('cd', complete_cd),
    ('rmdir', complete_rmdir),
    ('man', complete_from_man),
    ('import', complete_import),
    ('python', complete_python),
    ('path', complete_path),
])

builtins.__tako_completers__ = completers

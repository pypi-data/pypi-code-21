# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Console Stuff
"""

from __future__ import unicode_literals, absolute_import

import sys

import progressbar


class Progress(object):
    """
    Provides a console-based progress bar.
    """

    def __init__(self, message, maximum, stdout=None):
        self.stdout = stdout or sys.stderr
        self.stdout.write("\n{}...({:,d} total)\n".format(message, maximum))
        widgets = [progressbar.Percentage(), ' ', progressbar.Bar(), ' ', progressbar.ETA()]
        self.progress = progressbar.ProgressBar(maxval=maximum, widgets=widgets).start()

    def update(self, value):
        self.progress.update(value)
        return True

    def destroy(self):
        self.stdout.write("\n")

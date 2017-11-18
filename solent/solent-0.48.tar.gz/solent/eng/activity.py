#
# activity
#
# // overview
# During the execution of the select loop, we want to know whenever activity
# occurs. This will affect the timeout of the next round of the select loop.
# We would track such activity in instances of this class.
#
# // license
# Copyright 2016, Free Software Foundation.
#
# This file is part of Solent.
#
# Solent is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Solent is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Solent. If not, see <http://www.gnu.org/licenses/>.

class Activity:
    def __init__(self):
        self.lst = []
    def clear(self):
        self.lst = []
    def mark(self, l, s):
        '''l: location; s: string description'''
        self.lst.append("%s/%s"%(str(l), s))
    def get(self):
        return self.lst[:]

def activity_new():
    ob = Activity()
    return ob


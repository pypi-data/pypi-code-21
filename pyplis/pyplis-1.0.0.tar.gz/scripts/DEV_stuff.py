# -*- coding: utf-8 -*-
#
# Pyplis is a Python library for the analysis of UV SO2 camera data
# Copyright (C) 2017 Jonas Gliß (jonasgliss@gmail.com)
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License a
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

def update_dict(d, info_dict, **kwargs):
    for key, val in info_dict.iteritems():
            if key in d.keys() and val is not None:
                d[key] = val
                
    d.update(**kwargs)
    return d

d = {"a"  :   1,
     "b"  :   2,
     "c"  :   3,
     "d"  :   4}

d = update_dict(d, info_dict={"a" : 11, "Bla":3}, c=33)

print d
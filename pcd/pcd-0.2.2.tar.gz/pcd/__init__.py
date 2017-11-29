## INFO ##
## INFO ##
"""
pcd - Python Contract Decorator
-------------------------------
Copyright (C) 2017 Peter Varo <hello@petervaro.com>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__all__ = 'contract', 'Invariant'


#------------------------------------------------------------------------------#
if __debug__:
    from pcd._invariant import Invariant
    from pcd._contract  import contract
else:
    class Invariant(type):
        def __new__(self, class_name, base_classes, attributes, *a, **k):
            attributes.pop('_{}__invariant'.format(class_name), None)
            return super(Invariant, self).__new__(
                self, class_name, base_classes, attributes)
    def contract(*args, **kwargs):
        def decorator(function):
            return function
        return decorator

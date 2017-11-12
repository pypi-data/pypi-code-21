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
DataSync Utilities
"""

from __future__ import unicode_literals, absolute_import

from sqlalchemy import orm


def make_dependency_sorter(model):
    """
    Return a function suitable for use when sorting data model class names,
    according to the underlying foreign key dependencies between the tables.
    """

    def depends_on(mapper_x, mapper_y, visited=set()):
        """
        Returns True if model 'x' has a (in)direct FK dependency on 'y', else False.
        """
        # First check for direct FK dependency.
        for column in mapper_x.columns:
            for fkey in column.foreign_keys:
                if fkey.column.table in mapper_y.tables:
                    return True

        # Must keep track of where we're been, to avoid infinite recursion in
        # the case of mutually-dependent tables.
        visited.add(mapper_x)

        # Next check recursively, for indirect FK dependency.
        for prop in mapper_x.iterate_properties:
            if isinstance(prop, orm.RelationshipProperty):
                if prop.direction.name == 'MANYTOONE':
                    if prop.mapper not in visited:
                        if depends_on(prop.mapper, mapper_y, visited=visited):
                            return True

        return False

    def dependency_sorter(x, y):
        """
        This function is meant to be used as the ``cmp`` kwarg to a standard
        Python sorting function.
        """
        map_x = orm.class_mapper(getattr(model, x))
        map_y = orm.class_mapper(getattr(model, y))

        # Check to see if one model depends (in)directly on the other.  If "x
        # depends on y" then we consider "x > y" and hence the final sort
        # result would be (y, x).  Note however that in the case of mutually
        # dependent tables, we must remain neutral and allow the tie.
        dep_x = depends_on(map_x, map_y)
        dep_y = depends_on(map_y, map_x)
        if dep_x and not dep_y:
            return 1
        if dep_y and not dep_x:
            return -1
        return 0

    return dependency_sorter

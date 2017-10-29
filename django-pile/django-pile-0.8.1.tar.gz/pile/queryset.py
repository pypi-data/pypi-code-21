#
# Copyright (C) 2014, Xavier Ordoquy (Modified BSD License)
#               2014, Martin Owens (AGPLv3)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
A base class for querysets that support being converted to managers
(for use as a model's `objects` manager) via `ManagerQuerySet.as_manager`.
"""

from django.db.models import Manager
from django.db.models.query import QuerySet

import inspect
import new

__all__ = ('ManagerQuerySet',)

class ManagerQuerySet(QuerySet):
    def as_manager(self, base=Manager):
        """
        Creates a manager from the queryset by copying any methods not
        defined in the queryset class's parent classes (`query.QuerySet` and
        `ManagerQuerySet`).
        """
        cls = self.__class__ # Nested class.
         
        class QuerySetManager(base):
            use_for_related_fields = True
             
            def get_query_set(self):
                return cls(self.model)
         
        base_classes = [ManagerQuerySet, QuerySet]
        base_methods = [
            inspect.getmembers(base, inspect.ismethod) for base in base_classes
        ]
         
        def in_base_class(method_name):
            for methods in base_methods:
                for (name, _) in methods:
                    if name == method_name:
                        return True
            return False
         
        for (method_name, method) in inspect.getmembers(self, inspect.ismethod):
             if not in_base_class(method_name):
                 new_method = new.instancemethod(
                     method.im_func, None, QuerySetManager
                 )
                 setattr(QuerySetManager, method_name, new_method)
     
        return QuerySetManager()


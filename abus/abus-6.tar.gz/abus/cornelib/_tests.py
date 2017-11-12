# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import unittest
from .misc import set_indentation, cog_make_struct_type

class _Cornelib_Tests_(unittest.TestCase):
   def test_set_indentation(self):
      self.assertEqual(set_indentation(0, "\n  two \n   three\n"), "two\n three")
      self.assertEqual(set_indentation(0, "\n  two \n\n   three\n"), "two\n\n three")
   def test_cog_make_struct_type(self):
      docstring= """
               Defines the way to update a single database column when data is being saved. Any names included in braces
               denote display column names and are replaced with values from changed display data.

               Args:
                  where_clause (unicode): clause following where keyword that defines row to be updated (from display columns)
                  uses_grid_columns (frozenset[unicode]): list of display column used in set_clause (used for determining quickly whether
                     this UpdateColumnDef needs to be included in an updated, given changed display columns.
               """
      expected= set_indentation(0, '''
         class UpdateColumnDef(object):
            # This is cog-generated code, make changes in the cog-comment above.
            @property
            def where_clause(self):
               return self._where_clause
            @property
            def uses_grid_columns(self):
               return self._uses_grid_columns
            def __repr__(self):
               fields= ", ".join([
                     "where_clause="+repr(self._where_clause),
                     "uses_grid_columns="+repr(self._uses_grid_columns),
                  ])
               return "UpdateColumnDef({})".format(fields)
            # noinspection PyProtectedMember
            def __eq__(self, other):
               return (isinstance(other, type(self))
                  and self._where_clause == other._where_clause
                  and self._uses_grid_columns == other._uses_grid_columns
                  )
            def __init__(self,
                         where_clause,
                         uses_grid_columns,
                         ):
               """''' + docstring+ '''"""
               self._where_clause= where_clause
               self._uses_grid_columns= uses_grid_columns
               assert isinstance(where_clause, unicode)
               assert isinstance(uses_grid_columns, frozenset)''')
      result= []
      cog_make_struct_type(lambda l: result.append(l), "UpdateColumnDef", docstring)
      actual= '\n'.join(result)
      self.maxDiff= None
      self.assertEqual(actual, expected)

if __name__=="__main__":
   unittest.main()

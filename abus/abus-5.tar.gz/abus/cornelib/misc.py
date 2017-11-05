# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import os
import re

def cog_make_struct_type(output_function, class_name, docstring):
   """
   Outputs code for immutable "struct" class. Result is without trailing newline.

   Include comments with calls to cog_make_struct_type() in some source file. Then run
   "cog.py -r source.py" over it. Cog can be installed with "pip install cogapp".

   Example:
      Only first occurrence needs the import and may define a function with a default for output_function::

      # [[[cog
      # import cornelib
      # make_struct= lambda cls,docstr: cornelib.cog_make_struct_type(cog.outl, cls, docstr)
      #
      # make_struct("Coord", '''
      # A two-dimensional coordinate.
      #
      # Args:
      #   x (float): x-value
      #   y (float): y-value counting up from bottom
      # ''')
      # ]]]
      class Coord(object):
         # This is cog-generated code, make changes in the cog-comment above.
         ...
      # [[[end]]]

   Args:
      class_name (unicode): name for new class
      docstring (unicode): for __init__ of new class.
         Lines in docstring starting "name (type):" define the class's fields.
         Indentation is irrelevant but must be consistent for all lines including the first one.
         May lead with a newline.
      output_function (lambda): function used to output one line (without newline), typically `cog.outl`
   """
   raw_code= r'''
      class CLASSNAME(object):
         # This is cog-generated code, make changes in the cog-comment above.
         @property               \
         def FIELDNAME(self):    \
            return self._FIELDNAME
         def __repr__(self):
            fields= ", ".join([
                  "FIELDNAME="+repr(self._FIELDNAME),
               ])
            return "CLASSNAME({})".format(fields)
         # noinspection PyProtectedMember
         def __eq__(self, other):
            return (isinstance(other, type(self))
               and self._FIELDNAME == other._FIELDNAME
               )
         def __init__(self,
                      FIELDNAME,
                      ):
            """
            DOCSTRING
            """
            self._FIELDNAME= FIELDNAME
            assert isinstance(FIELDNAME, FIELDTYPE)
      '''
   raw_code= set_indentation(0, raw_code)
   raw_code= raw_code.replace("CLASSNAME", class_name)
   raw_code= raw_code.replace("      DOCSTRING", set_indentation(6, docstring))
   fielddef= re.compile(r"^\s*(\w+)\s+\((\w+)(\[[^)]*)?\):")
   fielddef_matches= [fielddef.match(line) for line in docstring.split("\n")]
   fields= [ (m.group(1), m.group(2)) for m in fielddef_matches if m]
   carry= None
   for code_line in raw_code.split('\n'):
      if carry:
         code_line= carry +'\n' +code_line
         carry= None
      if code_line.endswith('\\'):
         carry= code_line[:-1].rstrip()
         continue
      code_line= code_line.rstrip()
      if "FIELDNAME" in code_line:
         for field_name, field_type in fields:
            output_function(code_line.replace("FIELDNAME", field_name).replace("FIELDTYPE", field_type))
      else:
         output_function(code_line)

def set_indentation(new_indentation, multi_line_string):
   """
   returns multi_line_string with
      - all trailing spaces stripped
      - all leading and trailing empty lines stripped
      - no final newline
      - smallest indentation set to `new_indentation`
   """
   assert '\t' not in multi_line_string
   lines= [l.rstrip() for l in multi_line_string.split('\n')]
   while not lines[0]:
      lines.pop(0)
   while not lines[-1]:
      lines.pop()
   spaces= re.compile("\s*")
   old_indentation= min(spaces.match(l).end() for l in lines if l)
   if new_indentation > old_indentation:
      pfx= ' ' * (new_indentation - old_indentation)
      lines= [pfx + l if l else "" for l in lines]
   elif new_indentation < old_indentation:
      cut= old_indentation - new_indentation
      lines= [l[cut:] for l in lines]
   return '\n'.join(lines).rstrip()

class partial_write_guard(object):
   def __init__(self, path:str):
      """
      Context manager protecting against leaving partially written files in case of error.
      Write to the path returned when entering; this will then be renamed to the given path,
      or deleted.

      :param path: the intended path for a file
      """
      self.path= path
      self.partial= path+".part"
   def __enter__(self):
      return self.partial
   def __exit__(self, exc_type, exc_val, exc_tb):
      if exc_type is None:
         os.rename(self.partial, self.path)
      else:
         os.unlink(self.partial)

#! /usr/bin/python
# -*- coding: utf-8 -*-

import pprint as pp
import sys

if sys.version_info[0] < 3:
  class UnicodePrinter(pp.PrettyPrinter):
    def format(self, object, context, maxlevels, level):
      """Overrided method to enable Unicode pretty print."""
      if isinstance(object, unicode):
        encoding = sys.stdout.encoding or 'utf-8'
        return object.encode(encoding), True, False
      return pp.PrettyPrinter.format(self, object, context, maxlevels, level)

if sys.version_info[0] < 3:
  def pprint(obj):
    """Unicode pretty printer."""
    return UnicodePrinter().pprint(obj)
else:
  pprint = pp.pprint
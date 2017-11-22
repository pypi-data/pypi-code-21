from __future__ import absolute_import, division, print_function

__version__ = "0.13"

def jiradls():
  # Shortcut to create a Diamond JIRA object.
  import jiradls.dlsjira
  return jiradls.dlsjira.DLSJIRA()

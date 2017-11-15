from __future__ import absolute_import, division, print_function

import re

employee = {
 'gw': 'gw56',
 'is': 'voo82357',
 'mg': 'wra62962',
 'rjg': 'hko55533',
 'rg': 'hko55533',
}

re_is_number = re.compile('^\d+$')
re_is_issue = re.compile('^([a-zA-Z][a-zA-Z0-9_]*)-(\d+)$')

def issue_number(candidate):
  '''Take a string and see if it represents a issue or can be interpreted as
     such. If so, return fully qualified issue name.'''

  if not candidate: return False

  is_number = re_is_number.match(candidate)
  if is_number:
    candidate = int(candidate)
    if candidate < 1000:
      print("Did you mean SCRATCH-{}? Not touching this ticket number".format(candidate))
      return False
    return "SCI-%d" % candidate

  is_issue = re_is_issue.match(candidate)
  if is_issue:
    return candidate   # is already a fully qualified issue name

  print("{} is not a valid ticket".format(candidate))
  return False   # Do not know what this is.


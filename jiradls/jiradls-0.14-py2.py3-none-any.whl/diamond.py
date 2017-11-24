from __future__ import absolute_import, division, print_function

import datetime
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
    return candidate.upper()  # is already a fully qualified issue name

  print("{} is not a valid ticket".format(candidate))
  return False   # Do not know what this is.

def run_number():
  try:
    with open('/home/ops/scripts/python/displayScreens/stats/statsConfig.txt', 'r') as fh:
      return int(re.match("^S'([0-9]+)'", fh.readline()).group(1))
  except Exception:
    return 0

def filter_versions(versions, run=None, year=None, return_map=False):
  if not run:
    run = 0
  if not year:
    year = datetime.datetime.today().year
  rf = re.compile('^(Run|Shutdown) ([0-9]+) \(([0-9]{4})\)$')

  def filter_version(version):
    m = rf.match(version)
    if not m:
      return False
    if int(m.group(3)) < year:
      return False # run/shutdowns from previous years
    if int(m.group(3)) > year:
      return True  # run/shutdowns for future years
    if int(m.group(2)) < run:
      return False # run/shutdowns earlier this year
    return True    # run/shutdowns currently and later this year
  versions = filter(filter_version, versions)
  if not return_map:
    return list(versions)

  version_map = {}
  for version in versions:
    m = rf.match(version)
    key = m.group(1).lower() + m.group(2)
    if key in version_map:
      version_map[key] = min(version_map[key], version) # any given number identifies the earlier run/shutdown
    else:
      version_map[key] = version
  return version_map

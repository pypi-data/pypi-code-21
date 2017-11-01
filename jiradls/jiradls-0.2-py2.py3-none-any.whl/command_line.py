from __future__ import absolute_import, division, print_function

from jiradls.dlsjira import DLSJIRA

def main():
  jira = DLSJIRA()
  i30 = jira.issue('SCRATCH-30')
  print(str(i30))
  print(i30.fields.summary)

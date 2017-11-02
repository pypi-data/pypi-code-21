from __future__ import absolute_import, division, print_function

import sys

from jiradls.dlsjira import DLSJIRA

class iJIRA(object):
  def __init__(self):
    self._jira = None

  def jira(self):
    if not self._jira:
      self._jira = DLSJIRA()
    return self._jira

  def do(self, words):
    if not words or words[0] == '':
      return self.do_help()
    func = getattr(self, 'do_' + words[0].lower())
    if func:
      return func(words[1:])
    {
      'help': self.do_help,
    }.get(words[0].lower(), 'help')(words[1:])

  def do_help(self, *args):
    print("Welcome to the JIRA cli. Try\n  $ jira list")

  def do_list(self, words=None):
    all_my_issues = self.jira().search_issues('assignee = currentUser() AND resolution = unresolved ORDER BY RANK ASC')
    if all_my_issues.total == len(all_my_issues):
      print("Your open issues are:")
    else:
      print("Here are {num} out of your {total} open issues:".format(num=len(all_my_issues), total=all_my_issues.total))
    print()
    for i in all_my_issues:
      print("{}: {}".format(i, i.fields.summary))

  def do_add(self, words=None):
    fields = {
      'project': 'SCRATCH',
      'summary': [],
      'description': '',
      'issuetype': { 'name': 'Minor Task/Bug' },
      'components': [{ 'name': 'Scisoft MX' }],
      'assignee': None,
    }

    priorities = { 'crit': 'Critical', 'critical': 'Critical', 'major': 'Major', 'maj': 'Major', 'minor': 'Minor' }

    parsing = True
    for n, w in enumerate(words):
      l = w.lower()
#     print((n, w))
      if w.startswith('@') and fields['assignee'] is None: # Assign user
        if l[1:] in ('gw'):
          fields['assignee'] = 'gw56'
          continue
        if l[1:] in ('mg'):
          fields['assignee'] = 'wra62962'
          continue
        if l[1:] in ('rg', 'rjg'):
          fields['assignee'] = 'hko55533'
          continue
        if l[1:] in ('is'):
          fields['assignee'] = 'voo82357'
          continue
        if n < (len(words)-1):
          fields['assignee'] = l[1:]
          continue
      if l in priorities:
        fields['priority'] = { 'name': priorities[l] }
        continue
      if l == 'sci':
        fields['project'] = 'SCI'
        fields['components'] = []
        continue
      break
#   print(n)

    fields['summary'] = ' '.join(words[n:])
    if fields['assignee']:
      fields['assignee'] = { 'name': fields['assignee'] }

#   from pprint import pprint
#   pprint(fields)
    issue = self.jira().create_issue(fields=fields)
    print("Ticket {} created".format(issue))

  def do_do(self, words):
    for ticket in words:
      if '-' not in ticket:
        ticket = 'SCRATCH-' + ticket
      issue = self.jira().issue(ticket)
      if issue.fields.status.name == 'In Progress':
        print("Ticket {} already in progress.".format(ticket))
        continue
      transitions = self.jira().transitions(issue)
      transitions = { t['name'].lower(): t['id'] for t in transitions }
      if 'start work' in transitions:
        self.jira().transition_issue(issue, transitions['start work'])
        print("Ticket {} in progress.".format(ticket))
      else:
        print("Could not start work on ticket {}, available transitions: {}".format(ticket, list(transitions)))

  def do_done(self, words):
    for ticket in words:
      if '-' not in ticket:
        ticket = 'SCRATCH-' + ticket
      issue = self.jira().issue(ticket)
      if issue.fields.status.name == 'Wait Deploy':
        print("Ticket {} already waiting for deployment.".format(ticket))
        continue
      transitions = self.jira().transitions(issue)
      transitions = { t['name'].lower(): t['id'] for t in transitions }
      if 'await deployment' in transitions:
        self.jira().transition_issue(issue, transitions['await deployment'])
        print("Ticket {} awaiting deployment.".format(ticket))
      else:
        print("Could not mark ticket {} as done, available transitions: {}".format(ticket, list(transitions)))

  def do_close(self, words):
    for ticket in words:
      if '-' not in ticket:
        ticket = 'SCRATCH-' + ticket
      issue = self.jira().issue(ticket)
      if issue.fields.status.name in ('Resolved', 'Closed'):
        print("Ticket {} already closed.".format(ticket))
        continue
      transitions = self.jira().transitions(issue)
      transitions = { t['name'].lower(): t['id'] for t in transitions }
      if 'close' in transitions:
        self.jira().transition_issue(issue, transitions['close'], resolution={'name': 'Completed'})
        print("Ticket {} closed.".format(ticket))
      else:
        print("Could not close ticket {}, available transitions: {}".format(ticket, list(transitions)))

def main():
  iJIRA().do(sys.argv[1:])

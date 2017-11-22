from __future__ import absolute_import, division, print_function

import os
import re
import subprocess
import sys
import tempfile

import jiradls.diamond
import jiradls.workflow
import six
from colorama import Fore, Style

colors = {
  'bold': Style.RESET_ALL + Style.BRIGHT,
  'dim': Style.DIM,
  'reset': Style.RESET_ALL,
  'green': Fore.GREEN + Style.BRIGHT,
}

class iJIRA(object):
  def __init__(self):
    self._jira = None
    self._aliases = {
      'say': 'comment',
      'do': 'work',
      'done': 'close',
      'open': 'todo',
      'reassign': 'assign',
      'stuck': 'block',
      'sub': 'subtask',
      'unstuck': 'unblock',
    }

  def jira(self):
    if not self._jira:
      self._jira = jiradls.jiradls()
    return self._jira

  def do(self, words):
    if not words or words[0] == '':
      return self.do_help()
    command = words[0].lower()
    command = self._aliases.get(command, command)
    try:
      func = getattr(self, 'do_' + command)
    except AttributeError:
      return print("Unknown command '{}'. Run with\n   $ jira\nto see what is possible.".format(command))
    return func(words[1:])

  def do_help(self, *args):
    '''Shows command line help.'''
    print("JIRA command line interface v{}\n".format(jiradls.__version__))
    for f in sorted(dir(self)):
      if f.startswith('do_'):
        command = f.replace('do_', 'jira ')
        text = getattr(self, f).__doc__
        if text:
          text = text.strip(' \t\n\r').split('\n', 1)
          print("{green}{command} - {bold}{text[0]}{reset}".format(
            command=command, text=text, **colors))
          indent = ' ' * (len(command) + 3)
          aliases = [ "jira " + k for k in self._aliases if self._aliases[k] == f[3:] ]
          if aliases:
            plural = 'es' if len(aliases) > 1 else ''
            print("{indent}(also: {green}{list}{reset})".format(indent=indent, plural=plural, list="{reset}, {green}".join(aliases), **colors))
          if len(text) > 1:
            indent = ' ' * (len(command) + 3)
            body = text[1].strip(' \t\n\r').split('\n')
            print("{indent}{body}".format(indent=indent, body=('\n' + indent).join(body)))
          print()

  def do_list(self, words=None):
    '''Shows a list of all your issues

       This is currently unsorted and limited to 50 issues.
    '''
    all_my_issues = self.jira().search_issues('assignee = currentUser() AND resolution = unresolved ORDER BY RANK ASC')
    if all_my_issues.total == len(all_my_issues):
      print("Your open issues are:")
    else:
      print("Here are {num} out of your {total} open issues:".format(num=len(all_my_issues), total=all_my_issues.total))
    print()
    for i in all_my_issues:
      print("{}: {}".format(i, i.fields.summary))

  def do_add(self, words=None):
    '''Create a new ticket'''
    fields = {
      'project': 'SCI',
      'summary': [],
      'description': '',
      'issuetype': { 'name': 'Minor Task/Bug' },
      'labels': [ 'MXSW' ],
      'components': [],
      'assignee': None,
    }

    priorities = { 'crit': 'Critical', 'critical': 'Critical', 'major': 'Major', 'maj': 'Major', 'minor': 'Minor' }

    parsing = True
    for n, w in enumerate(words):
      l = w.lower()
#     print((n, w))
      if w.startswith('@') and fields['assignee'] is None: # Assign user
        if l[1:] in jiradls.diamond.employee:
          fields['assignee'] = jiradls.diamond.employee[l[1:]]
          continue
        if n < (len(words)-1):
          fields['assignee'] = l[1:]
          continue
      if l in priorities:
        fields['priority'] = { 'name': priorities[l] }
        continue
      if l == 'scratch':
        fields['project'] = 'SCRATCH'
        fields['components'] = [{ 'name': 'Scisoft MX' }]
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

  def do_subtask(self, words):
    '''Create a subtask for an existing ticket.'''
    ticket = jiradls.diamond.issue_number(words[0])
    if not ticket: return
    words = words[1:]

    fields = {
      'project': ticket.split('-')[0],
      'parent': { 'key': ticket },
      'summary': [],
      'description': '',
      'issuetype': { 'name': 'Sub-task' },
      'labels': [ 'MXSW' ],
      'components': [],
      'assignee': None,
    }

    priorities = { 'crit': 'Critical', 'critical': 'Critical', 'major': 'Major', 'maj': 'Major', 'minor': 'Minor' }

    parsing = True
    for n, w in enumerate(words):
      l = w.lower()
#     print((n, w))
      if w.startswith('@') and fields['assignee'] is None: # Assign user
        if l[1:] in jiradls.diamond.employee:
          fields['assignee'] = jiradls.diamond.employee[l[1:]]
          continue
        if n < (len(words)-1):
          fields['assignee'] = l[1:]
          continue
      if l in priorities:
        fields['priority'] = { 'name': priorities[l] }
        continue
      if l == 'scratch':
        fields['project'] = 'SCRATCH'
        fields['components'] = [{ 'name': 'Scisoft MX' }]
        continue
      break
#   print(n)

    fields['summary'] = ' '.join(words[n:])
    if fields['assignee']:
      fields['assignee'] = { 'name': fields['assignee'] }

    issue = self.jira().create_issue(fields=fields)
    print("Ticket {} created as subtask of {}".format(issue, ticket))

  def transition_to(self, ticket, target, maxdepth=3):
    # Convert targets into a list of IDs
    if isinstance(target, (int, six.string_types)):
      target = [target]
    target = [t if isinstance(t, int) else jiradls.workflow.status_id[t.lower()] for t in target]

    # Obtain current status as ID
    issue = self.jira().issue(ticket)
    current_status = jiradls.workflow.status_id[issue.fields.status.name.lower()]

    if current_status in target:
      return None # We are already there.

    routes = jiradls.workflow.route_workflow(current_status, target)
    if not routes:
      return False # There is no route from here to there.

    transitions = self.jira().transitions(issue)
    transitions = { jiradls.workflow.status_id[t['to']['name'].lower()]: t for t in transitions }
#   print("Status: {}".format(issue.fields.status.name))
#   print("Target: {}".format(target))

    selected_route = None
    for r in routes:
      if r[0] == current_status and r[1] in transitions:
        selected_route = r
        break
    if not selected_route:
      return False # There is no valid route from here to there.
 #  print("Route: {}".format(selected_route))
    print("{issue}: {transition}".format(issue=issue, transition=transitions[selected_route[1]]['name']))

    transition_fields = {}
    if transitions[selected_route[1]]['name'].lower() in jiradls.workflow.closing_resolutions:
      transition_fields['resolution'] = { 'name': jiradls.workflow.closing_resolutions[transitions[selected_route[1]]['name'].lower()] }
    self.jira().transition_issue(issue, transitions[selected_route[1]]['id'], fields=transition_fields)

    if len(selected_route) <= 2:
      # This was a direct route. We're done
      return True

    # This was not a direct route, so recurse (up to maxdepth levels)
    if maxdepth > 0:
#     print("Recursing to {} {}".format(issue, target))
      return self.transition_to(ticket, target, maxdepth-1)

    # Recursion failure
    print("Recursion failure")
    return False

  def do_work(self, words):
    """Mark ticket as 'in progress'"""
    for ticket in words:
      ticket = jiradls.diamond.issue_number(ticket)
      if not ticket: continue
      print({ None: "Ticket {} already in progress.",
              True: "Ticket {} in progress.",
      }.get(self.transition_to(ticket, ('In Progress', 'Active')),
                    "Could not start work on ticket {}").format(ticket))

  def do_wait(self, words):
    """Mark ticket as 'waiting for deployment'"""
    for ticket in words:
      ticket = jiradls.diamond.issue_number(ticket)
      if not ticket: continue
      print({ None: "Ticket {} already waiting for deployment.",
              True: "Ticket {} waiting for deployment.",
      }.get(self.transition_to(ticket, ('Validation', 'Wait Deploy')),
                    "Could not mark ticket {} as waiting for deployment").format(ticket))

  def do_close(self, words):
    """Close a ticket"""
    for ticket in words:
      ticket = jiradls.diamond.issue_number(ticket)
      if not ticket: continue
      issue = self.jira().issue(ticket, fields='customfield_10010')
      if issue.fields.customfield_10010:
        # If ticket is blocked, try to unblock it before closing
        try:
          issue.update(fields={'customfield_10010': None})
          print("marked %s as unblocked" % ticket)
        except jira.exceptions.JIRAError:
          print("could not mark %s as unblocked" % ticket)
      print({ None: "Ticket {} already closed.",
              True: "Ticket {} closed.",
      }.get(self.transition_to(ticket, ('Resolved', 'Closed')),
                    "Could not close ticket {}").format(ticket))

  def do_todo(self, words):
    """Reset ticket into open (to do) state"""
    for ticket in words:
      ticket = jiradls.diamond.issue_number(ticket)
      if not ticket: continue
      print({ None: "Ticket {} already open.",
              True: "Ticket {} opened.",
      }.get(self.transition_to(ticket, ('Open', 'Deferred')),
                    "Could not open ticket {}").format(ticket))

  def do_comment(self, words):
    """Add a comment to a ticket"""
    ticket = jiradls.diamond.issue_number(words[0])
    if not ticket: return
    comment = " ".join(words[1:])
    if not comment:
      try:
        fd, tmpfile = tempfile.mkstemp()
        with open(tmpfile, 'w') as fh:
          fh.write('\n\n### {ticket} - {summary}\n'.format(ticket=ticket, summary=self.jira().issue(ticket).fields.summary))
          fh.write('### Text above will be added to the ticket as comment.\n')
          fh.write('### Quit editor without saving to abort.\n')
        os.close(fd)
        returncode = subprocess.call(['vim', tmpfile])
        if not returncode:
          comment = []
          with open(tmpfile, 'r') as fh:
            for line in fh:
              if not line.strip().startswith('###'):
                comment.append(line)
          comment = ''.join(comment).strip()
      finally:
        os.remove(tmpfile)
    if comment:
      self.jira().add_comment(ticket, comment)
      print("Added comment to", ticket)

  def do_assign(self, words):
    """Assign ticket(s) to another user"""
    user = words[0].lower()
    if not user.startswith('@'):
      print("Pass username with leading '@' first, followed by list of ticket IDs.")
      return
    assignee = jiradls.diamond.employee.get(user[1:], user[1:])
    for ticket in words[1:]:
      ticket = jiradls.diamond.issue_number(ticket)
      if not ticket: continue
      print({ True: "Ticket {ticket} assigned to {assignee}",
        }.get(self.jira().assign_issue(ticket, assignee),
              "Could not assign ticket {ticket} to {assignee}") \
        .format(ticket=ticket, assignee=assignee))

  def do_unassign(self, words):
    """Remove assigned user from ticket(s)"""
    for ticket in words:
      ticket = jiradls.diamond.issue_number(ticket)
      if not ticket: continue
      print({ True: "Ticket {ticket} unassigned",
        }.get(self.jira().assign_issue(ticket, '-1'),
              "Could not unassign ticket {ticket}") \
        .format(ticket=ticket))

  def do_block(self, words):
    """Mark a ticket as blocked/stuck"""
    for ticket in words:
      ticket = jiradls.diamond.issue_number(ticket)
      if not ticket: continue
      print("marking %s as blocked" % ticket)
      self.jira().issue(ticket).update(fields={'customfield_10010': [ { 'id': '10000' } ] })

  def do_unblock(self, words):
    """Mark a ticket as no longer blocked/stuck"""
    for ticket in words:
      ticket = jiradls.diamond.issue_number(ticket)
      if not ticket: continue
      print("marking %s as unblocked" % ticket)
      self.jira().issue(ticket).update(fields={'customfield_10010': None})

  def do_priority(self, words):
    """Change ticket priority
       (trivial = lowest, minor = low, normal, major = high, critical = highest)"""
    priorities = { 't': 'Trivial', 'mi': 'Minor', 'n': 'Normal', 'ma': 'Major', 'c': 'Critical',
                   'h': 'Major', 'highe': 'Critical', 'l': 'Minor', 'lowe': 'Trivial' }
    target_priority = words[0].lower()
    possible_priorities = filter(lambda x: target_priority.startswith(x), list(priorities))
    if not possible_priorities or '-' in target_priority:
      print("'%s' is not a valid priority (trivial = lowest, minor = low, normal, major = high, critical = highest)" % target_priority)
      return 
    target_priority = priorities.get(max(possible_priorities, key=len))
    for ticket in words[1:]:
      ticket = jiradls.diamond.issue_number(ticket)
      if not ticket: continue
      print("Changing priority of %s to %s" % (ticket, target_priority))
      self.jira().issue(ticket).update(fields={'priority': { 'name': target_priority }})

  def do_plan(self, words):
    """Plan a ticket for an upcoming run or shutdown"""
    runlabels, tickets = [], []
    plan = re.compile('^([a-z]+)([0-9]?)$')
    for word in words:
      runlabel = plan.match(word)
      if runlabel:
        if runlabel.group(1) == 'run'[:len(runlabel.group(1))]:
          runlabels.append('run' + runlabel.group(2))
          continue
        elif runlabel.group(1) == 'shutdown'[:len(runlabel.group(1))]:
          runlabels.append('shutdown' + runlabel.group(2))
          continue
      ticket = jiradls.diamond.issue_number(word)
      if ticket:
        tickets.append(ticket)
        continue
      print("Do not understand '%s'. It does not refer to a run or a shutdown number or a ticket number." % word)
      return
    print("Command not yet implemented, but would set labels {} for tickets {}".format(runlabels, tickets))

def main():
  iJIRA().do(sys.argv[1:])

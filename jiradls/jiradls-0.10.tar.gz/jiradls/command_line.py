from __future__ import absolute_import, division, print_function

import sys

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
      'todo': 'open',
      'reassign': 'assign',
      'stuck': 'block',
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
      if '-' not in ticket:
        if int(ticket) < 100:
          print("Did you mean SCRATCH-{}? Default is now to use the 'SCI-' namespace. Not touching ticket!".format(ticket))
          return
        ticket = 'SCI-' + ticket
      print({ None: "Ticket {} already in progress.",
              True: "Ticket {} in progress.",
      }.get(self.transition_to(ticket, ('In Progress', 'Active')),
                    "Could not start work on ticket {}").format(ticket))

  def do_wait(self, words):
    """Mark ticket as 'waiting for deployment'"""
    for ticket in words:
      if '-' not in ticket:
        if int(ticket) < 100:
          print("Did you mean SCRATCH-{}? Default is now to use the 'SCI-' namespace. Not touching ticket!".format(ticket))
          return
        ticket = 'SCI-' + ticket
      print({ None: "Ticket {} already waiting for deployment.",
              True: "Ticket {} waiting for deployment.",
      }.get(self.transition_to(ticket, ('Validation', 'Wait Deploy')),
                    "Could not mark ticket {} as waiting for deployment").format(ticket))

  def do_close(self, words):
    """Close a ticket"""
    for ticket in words:
      if '-' not in ticket:
        if int(ticket) < 100:
          print("Did you mean SCRATCH-{}? Default is now to use the 'SCI-' namespace. Not touching ticket!".format(ticket))
          return
        ticket = 'SCI-' + ticket
      print({ None: "Ticket {} already closed.",
              True: "Ticket {} closed.",
      }.get(self.transition_to(ticket, ('Resolved', 'Closed')),
                    "Could not close ticket {}").format(ticket))

  def do_open(self, words):
    """Reset ticket into open state"""
    for ticket in words:
      if '-' not in ticket:
        if int(ticket) < 100:
          print("Did you mean SCRATCH-{}? Default is now to use the 'SCI-' namespace. Not touching ticket!".format(ticket))
          return
        ticket = 'SCI-' + ticket
      print({ None: "Ticket {} already open.",
              True: "Ticket {} opened.",
      }.get(self.transition_to(ticket, ('Open', 'Deferred')),
                    "Could not open ticket {}").format(ticket))

  def do_comment(self, words):
    """Add a comment to a ticket"""
    ticket = words[0]
    if '-' not in ticket:
      ticket = 'SCI-' + ticket
    comment = " ".join(words[1:])
    self.jira().add_comment(ticket, comment)

  def do_assign(self, words):
    """Assign ticket(s) to another user"""
    user = words[0].lower()
    if not user.startswith('@'):
      print("Pass username with leading '@' first, followed by list of ticket IDs.")
      return
    assignee = jiradls.diamond.employee.get(user[1:], user[1:])
    for ticket in words[1:]:
      if '-' not in ticket:
        ticket = 'SCI-' + ticket
      print({ True: "Ticket {ticket} assigned to {assignee}",
        }.get(self.jira().assign_issue(ticket, assignee),
              "Could not assign ticket {ticket} to {assignee}") \
        .format(ticket=ticket, assignee=assignee))

  def do_block(self, words):
    """Mark a ticket as blocked/stuck"""
    ticket = words[0]
    if '-' not in ticket:
      ticket = 'SCI-' + ticket
    comment = " ".join(words[1:])
    self.jira().issue(ticket).update(fields={'customfield_10010': [ { 'id': '10000' } ] })

  def do_unblock(self, words):
    """Mark a ticket as no longer blocked/stuck"""
    ticket = words[0]
    if '-' not in ticket:
      ticket = 'SCI-' + ticket
    comment = " ".join(words[1:])
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
      if '-' not in ticket:
        ticket = 'SCI-' + ticket
      print("Changing priority of %s to %s" % (ticket, target_priority))
      self.jira().issue(ticket).update(fields={'priority': { 'name': target_priority }})

def main():
  iJIRA().do(sys.argv[1:])

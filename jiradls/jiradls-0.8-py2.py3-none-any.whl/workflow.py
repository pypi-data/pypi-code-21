from __future__ import absolute_import, division, print_function

# Map status IDs to names
status_name = {
  1: 'open',
  2: 'deferred',
  3: 'active',
  4: 'analysis',
  5: 'development',
  6: 'validation',
  7: 'resolved',
  8: 'closed',
  9: 'wait deploy',
 10: 'in progress',
}

# Map status names to IDs
status_id = { status_name[i]: i for i in status_name }

# Default resolutions for closing tickets
closing_resolutions = {
  "resolve as don't do": "Non Issue",
  "resolve as done": "Completed",
  "close": "Done",
}

# Exhaustive list of all allowed status transitions in (Diamond workflow || Simple workflow)
transitions = {
  1: [ 2, 3, 7, 8, 10 ],
  2: [ 1, 3, 7 ],
  3: [ 2, 4, 5, 6, 7 ],
  4: [ 3, 5, 6, 7 ],
  5: [ 3, 4, 6, 7 ],
  6: [ 3, 4, 5, 7 ],
  7: [ 3, 8 ],
  8: [ 1 ],
  9: [ 8 ],
 10: [ 1, 8, 9 ],
}

def route_workflow(status_from, status_to, dont_pass=None):
  '''Find routes from one status ID to another.
     Destination can also be a list of equivalent nodes.'''

  if type(status_to) is not list:
    status_to = [ status_to ]

  if status_from in status_to: # path found
    return [ [status_from] ]

  routes = []
  if dont_pass is None:
    dont_pass = set()
  dont_pass = dont_pass | {status_from} # no cycles

  for node in transitions[status_from]:
    if node in dont_pass:
      continue
    else:
      for r in route_workflow(node, status_to, dont_pass):
        routes.append([status_from] + r)
  return sorted(routes, key=len)

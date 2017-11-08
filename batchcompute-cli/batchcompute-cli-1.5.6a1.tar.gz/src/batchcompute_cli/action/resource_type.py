
# -*- coding:utf-8 -*-

from terminal import bold, magenta
from ..util import list2table, client
import json

def list(show_json=False):
    # system disk types
    arr = client.get_quotas().AvailableClusterResourceType

    t = []
    for n in arr:
        t.append({'name':n})

    if show_json:
        print(json.dumps(t, indent=2))
        return

    print('%s' % bold(magenta('Resource Types:')))
    list2table.print_table(t, [('name', 'Name')], False)
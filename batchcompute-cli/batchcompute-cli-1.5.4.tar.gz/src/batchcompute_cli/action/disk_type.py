
# -*- coding:utf-8 -*-

from terminal import bold, magenta
from ..util import list2table, client
import json

def list(show_json=False):

    # system disk types
    arr = client.get_quotas().AvailableClusterInstanceSystemDiskType
    t = []
    for n in arr:
        t.append({'name':n})



    # data disk types
    arr2 = client.get_quotas().AvailableClusterInstanceDataDiskType
    t2 = []
    for n in arr2:
        t2.append({'name': n})

    if show_json:
        print(json.dumps({
            'SystemDiskTypes': t,
            'DataDiskTypes': t2
        }, indent=2))
        return

    print('%s' % bold(magenta('System Disk Types:')))
    list2table.print_table(t, [('name', 'Name')], False)


    print('%s' % bold(magenta('Data Disk Types:')))
    list2table.print_table(t2, [('name', 'Name')], False)
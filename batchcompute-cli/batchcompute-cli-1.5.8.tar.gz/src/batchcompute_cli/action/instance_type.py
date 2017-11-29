
# -*- coding:utf-8 -*-

from terminal import bold, magenta
from ..util import list2table, client
from ..const import CMD
import json


def list(show_json=False):

    it = client.list_instance_types() or []
    sit = client.list_spot_instance_types() or []

    if show_json:
        print(json.dumps({
            'InstanceTypes': it,
            'SpotInstanceTypes': sit
        },indent=2))
        return


    print('%s' % bold(magenta('Instance types:')))
    list2table.print_table(it, [('name','Name'),('cpu','CPU(Core)'),('memory','Memory(GB)')],False)

    print('%s' % bold(magenta('Spot Instance types:')))
    list2table.print_table(sit,
                           [('name', 'Name'), ('cpu', 'CPU(Core)'), ('memory', 'Memory(GB)')], False)

    print('\n  using "%s set -t <Name>" to set default instance type\n' % (CMD))
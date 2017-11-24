# -*- coding:utf-8 -*-

from terminal import bold, magenta

from batchcompute_sge.util import list2table
from batchcompute_sge.lib import batchcompute_client


def list_disks():
    quotas = batchcompute_client.get_quotas()

    # system disk types
    arr = quotas.AvailableClusterInstanceSystemDiskType
    t = []
    for n in arr:
        t.append({'name': n})

    print('%s' % bold(magenta('System Disk Types:')))
    list2table.print_table(t, [('name', 'Name')], False)

    # data disk types
    arr2 = quotas.AvailableClusterInstanceDataDiskType
    t2 = []
    for n in arr2:
        t2.append({'name': n})
    print('%s' % bold(magenta('Data Disk Types:')))
    list2table.print_table(t2, [('name', 'Name')], False)


def list_instance_types():
    print('%s' % bold(magenta('Instance types:')))
    list2table.print_table(batchcompute_client.list_instance_types(), [('name', 'Name'), ('cpu', 'CPU(Core)'), ('memory', 'Memory(GB)')], False)


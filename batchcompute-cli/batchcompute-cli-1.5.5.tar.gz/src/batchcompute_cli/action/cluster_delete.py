
# -*- coding:utf-8 -*-

from ..util import client, util, config
from terminal import bold, magenta, white, blue, green,red, yellow, confirm


def del_cluster(clusterId, yes=False):
    arr = clusterId.split(',')

    t = util.parse_id_arr(arr, 'clusters',True)

    if yes:
        __batch_del(t)
    else:
        try:
            if confirm("Delete all these clusters:\n%s \nAre you sure" % red('\n'.join(t)), default=False):
                __batch_del(t)
        except KeyboardInterrupt:
            print('')
            return


def __batch_del(arr):
    for item in arr:
        __del_cluster(item)

def __del_cluster(clusterId):
    print(white('exec: bcs delete_cluster %s' % clusterId))
    client.delete_cluster(clusterId)
    print(green('done'))

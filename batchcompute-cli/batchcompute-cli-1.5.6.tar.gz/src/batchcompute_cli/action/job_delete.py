
# -*- coding:utf-8 -*-
from batchcompute import ClientError

from ..util import client,config,util
from terminal import bold, magenta, white, blue, green,red, yellow, confirm
import re

PROGRESS_LEN = 50

def del_job(jobId, yes=False):
    arr = jobId.split(',')

    t = util.parse_id_arr(arr,'jobs',True)

    if yes:
        __batch_del(t)
    else:
        try:
            if confirm("Delete all these jobs:\n%s \nAre you sure" % red('\n'.join(t)), default=False):
                __batch_del(t)
        except KeyboardInterrupt:
            print('')
            return

def __batch_del(arr):
    for item in arr:
        __del_job(item)

def __del_job(jobId):
    print(white('exec: bcs delete_job %s' % jobId))
    try:
       client.stop_job(jobId)
    except ClientError as e:
        if e.code == 'StateConflict':
            pass
        else:
            raise e

    client.delete_job(jobId)
    print(green('done'))



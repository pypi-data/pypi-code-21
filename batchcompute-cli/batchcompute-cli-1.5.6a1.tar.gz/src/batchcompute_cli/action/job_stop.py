
# -*- coding:utf-8 -*-

from ..util import client,config,util
from terminal import bold, magenta, white, blue, green,red, yellow, confirm

PROGRESS_LEN = 50

def stop_job(jobId, yes=False):
    arr = jobId.split(',')

    t = util.parse_id_arr(arr,'jobs',True)

    if yes:
        __batch_stop(t)
    else:
        try:
            if confirm("stop all these jobs:\n%s \nAre you sure" % red('\n'.join(t)), default=False):
                __batch_stop(t)
        except KeyboardInterrupt:
            print('')
            return

def __batch_stop(arr):
    for item in arr:
        __stop_job(item)

def __stop_job(jobId):
    print(white('exec: bcs stop_job %s' % jobId))
    client.stop_job(jobId)
    print(green('done'))

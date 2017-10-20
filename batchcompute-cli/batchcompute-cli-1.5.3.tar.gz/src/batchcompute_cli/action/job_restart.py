
# -*- coding:utf-8 -*-

from ..util import client,config,util
from terminal import bold, magenta, white, blue, green,red, yellow, confirm

PROGRESS_LEN = 50

def restart_job(jobId, yes=False):
    arr = jobId.split(',')

    t = util.parse_id_arr(arr,'jobs',True)

    if yes:
        __batch_restart(t)
    else:
        try:
            if confirm("Restart all these jobs:\n%s \nAre you sure" % red('\n'.join(t)), default=False):
                __batch_restart(t)
        except KeyboardInterrupt:
            print('')
            return


def __batch_restart(arr):
    for item in arr:
        __restart_job(item)

def __restart_job(jobId):
    print(white('exec: bcs restart_job %s' % jobId))
    client.start_job(jobId)
    print(green('done'))

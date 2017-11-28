
# -*- coding:utf-8 -*-
from batchcompute import ClientError

from ..util import client,config,util,formater
from terminal import bold, magenta, white, blue, green,red, yellow, confirm
import re


def qdel(job_id, wait=None):

    if wait:
        raise Exception('Unsupported option: -W')

    jobId = formater.get_job_id(job_id)
    __del_job(jobId)

def __del_job(jobId):
    #print(white('exec: bcs delete_job %s' % jobId))
    try:
       client.stop_job(jobId)
    except ClientError as e:
        if e.code == 'StateConflict':
            pass
        else:
            raise e

    client.delete_job(jobId)
    print(green('done'))


# -*- coding:utf-8 -*-

from ..util import client, result_cache, config
from terminal import confirm,green


def update(jobId, priority=-1, yes=False):

    v = int(priority)
    if v < 1 or v > 1000:
        raise Exception('Invalid priority, it should be in scope [1..1000]')

    jobId = result_cache.get(jobId, 'jobs', True)


    if yes:
        client.change_job_priority(jobId, v)
        print(green('done'))
    else:
        if confirm('Change priority of %s' % jobId, default=False):
            client.change_job_priority(jobId, v)
            print(green('done'))

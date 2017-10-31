#!/usr/bin/env python
# coding: utf-8
# Author caijiajia.cn
# @ ALL RIGHTS RESERVED

import thread

from .job_register import JobRegister


class JobDispatcher(object):

    def dispatch(self, form, async=True):
        job_name = form['jobName']
        executor = JobRegister.instance().get_executor(job_name)
        if executor is not None:
            if async:
                thread.start_new(executor.execute_job, (form, ))
            else:
                executor.execute_job(form)
        else:
            pass  # should not be here
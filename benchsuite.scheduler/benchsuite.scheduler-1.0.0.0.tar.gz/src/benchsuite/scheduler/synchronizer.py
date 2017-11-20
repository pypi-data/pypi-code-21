# Benchmarking Suite
# Copyright 2014-2017 Engineering Ingegneria Informatica S.p.A.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Developed in the ARTIST EU project (www.artist-project.eu) and in the
# CloudPerfect EU project (https://cloudperfect.eu/)
import logging
from datetime import timedelta, datetime
from typing import List

from apscheduler.job import Job
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.interval import IntervalTrigger

from benchsuite.scheduler.schedules import BenchmarkingScheduleConfig, \
    BenchmarkingSchedulesDB

logger = logging.getLogger(__name__)


JOB_ID_PREFIX = 'ap-'

def __build_args_list(schedule):
    args = [schedule.username,
            schedule.provider_config_secret,
            schedule.tests]

    kwargs = {}

    if schedule.tags:
        kwargs['tags'] = schedule.tags

    if schedule.env:
        kwargs['env'] = schedule.env

    if schedule.additional_opts:
        kwargs['additional_opts'] = schedule.additional_opts

    return args, kwargs

def schedule_new_job(
        schedule: BenchmarkingScheduleConfig,
        scheduler: BaseScheduler):
    """
    schedule a new jobs starting from a schedule
    :param schedule:
    :param scheduler:
    :return:
    """

    assert schedule.interval, '"interval" field in the schedule cannot be None'

    id = JOB_ID_PREFIX + schedule.id
    trigger = IntervalTrigger(**schedule.interval)

    # import here to avoid import loops
    from benchsuite.scheduler.jobs.benchmarking import benchmarking_job

    j = scheduler.add_job(benchmarking_job, trigger=trigger, id=id,
                          args=[schedule],
                          jobstore='benchmarking_jobs',
                          max_instances=1,
                          coalesce=True,
                          # run immediately
                          next_run_time=datetime.now())

    logger.info('[ADD] Job %s with id %s added '
                'for schedule %s', str(j), j.id, schedule.id)


def update_job(job: Job, schedule: BenchmarkingSchedulesDB):
    """
    updates the scheduling interval and parameters of a scheduled jobs based on
    updated data in a schedule. The update is performed only if needed
    :param job:
    :param schedule:
    :return:
    """

    # update the interval if it is changed
    if job.trigger.interval != timedelta(**schedule.interval):
        logger.debug('[UPDATE] Job %s updated because interval '
                     'changed from "%s" to "%s"', job.id, job.trigger.interval,
                     timedelta(**schedule.interval))

        new_trigger = IntervalTrigger(**schedule.interval)
        job.reschedule(new_trigger)


    # update the parameters if changed
    if job.args[0] != schedule:
        logger.debug('[UPDATE] Job %s updated because the args '
                     'are changed', job.id)
        job.modify(args=[schedule])


def sync_jobs(
        schedules: List[BenchmarkingScheduleConfig],
        scheduler: BaseScheduler):
    """
    Syncrhonizes the scheduled jobs with the benchmarking schedules defined in
    the schedules database
    :param schedules:
    :param scheduler:
    :return:
    """

    logger.debug('Synchronizing benchmarking schedules with scheduler jobs')

    # convert from list to dict for easier access
    schedules = {s.id: s for s in schedules}

    # get all the jobs. Filter out jobs with an id not recognized as created
    # from the schedule
    jobs = {j.id[len(JOB_ID_PREFIX):]: j
            for j in scheduler.get_jobs() if j.id.startswith(JOB_ID_PREFIX)}

    logger.debug('Considering %s schedules and %s jobs',
                 len(schedules), len(jobs))

    # for all scheduled jobs...
    for id in jobs.keys():

        if id in schedules:
            # the scheduled jobs appears in the schedules db.
            # check if the parameters are the same otherwise, update it
            # (do not update always to avoid rescheduling and calls to the db)
            update_job(jobs[id], schedules[id])

        else:
            # the scheduled jobs does not exist in the schedules db
            # this means that it has been deleted from the schedules db and must
            # be deleted from here also
            logger.info('[REMOVE] Job %s removed '
                        'becasue not found in the schedules db', id)
            jobs[id].remove()

    # for all schedules...
    for id in schedules.keys():

        if id not in jobs:
            # the schedule does not appear in the scheduler jobs, it must be
            # added
            schedule_new_job(schedules[id], scheduler)

    logger.debug('Syncrhonization completed')
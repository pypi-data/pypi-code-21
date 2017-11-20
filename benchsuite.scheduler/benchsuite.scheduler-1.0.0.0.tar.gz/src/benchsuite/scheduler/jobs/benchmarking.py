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
from typing import Any

from benchsuite.scheduler.bsscheduler import get_bsscheduler
from benchsuite.scheduler.schedules import BenchmarkingScheduleConfig

logger = logging.getLogger(__name__)




class DockerJobFailedException(Exception):

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.retval = None
        self.log = None


def benchmarking_job(schedule: BenchmarkingScheduleConfig):

    logger.debug('Starting a benchmarking job')

    dockermanager = get_bsscheduler().dockermanager

    instance = dockermanager.create_benchsuite_multiexec_instance(schedule)

    retval, log = dockermanager.wait(instance)

    dockermanager.remove_instance(instance)

    if retval != 0:
        e = DockerJobFailedException(
            'The execution exit with status {0}'.format(retval))
        e.log = log
        raise e

    return retval


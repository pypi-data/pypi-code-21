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



DEFAULTS = {
    'SCHEDULES_SYNC_INTERVAL': 60,
    'SCHEDULES_JOBS_PRINT_INTERVAL': 60,

    'DB_HOST': None,
    'DB_NAME': 'benchmarking',

    'SCHEDULES_DB_HOST': None,
    'SCHEDULES_DB_NAME': None,
    'SCHEDULES_DB_COLLECTION': 'scheduling',

    'JOBS_DB_HOST': None,
    'JOBS_DB_NAME': None,
    'JOBS_DB_COLLECTION': '_apjobs',

    'EXEC_DB_HOST': None,
    'EXEC_DB_NAME': None,
    'EXEC_DB_COLLECTION': '_apexec',

    'DOCKER_HOST': 'localhost:2375',
    'DOCKER_STORAGE_SECRET': None,
    'DOCKER_BENCHSUITE_IMAGE': 'benchsuite/benchsuite-multiexec',
    'DOCKER_GLOBAL_ENV': {},
    'DOCKER_GLOBAL_TAGS': [],
    'DOCKER_ADDITIONAL_OPTS': []
}

class BenchsuiteSchedulerConfig(object):
    """the global configuration for the Benchsuite Scheduler"""

    def __init__(self, user_config):

        if 'DB_HOST' not in user_config and (
                        'SCHEDULES_DB_HOST' not in user_config or
                        'JOBS_DB_HOST' not in user_config or
                        'EXEC_DB_HOST' not in user_config):
            raise ValueError('Either DB_HOST or SCHEDULES_DB_HOST, '
                             'JOBS_DB_HOST and EXEC_DB_HOST are mandatory')

        if 'DOCKER_STORAGE_SECRET' not in user_config:
            raise ValueError('The DOCKER_STORAGE_SECRET config parameter '
                             'is mandatory.')

        # load defaults
        cfg = dict(DEFAULTS)

        # override with user values
        cfg.update(user_config)

        self.schedules_sync_interval = cfg['SCHEDULES_SYNC_INTERVAL']
        self.print_jobs_info_interval = cfg['SCHEDULES_JOBS_PRINT_INTERVAL']

        self.schedules_db_host = cfg['SCHEDULES_DB_HOST'] or cfg['DB_HOST']
        self.schedules_db_name = cfg['SCHEDULES_DB_NAME'] or cfg['DB_NAME']
        self.schedules_db_collection = cfg['SCHEDULES_DB_COLLECTION']

        self.jobs_db_host = cfg['JOBS_DB_HOST'] or cfg['DB_HOST']
        self.jobs_db_name = cfg['JOBS_DB_NAME'] or cfg['DB_NAME']
        self.jobs_db_collection = cfg['JOBS_DB_COLLECTION']

        self.exec_db_host = cfg['EXEC_DB_HOST'] or cfg['DB_HOST']
        self.exec_db_name = cfg['EXEC_DB_NAME'] or cfg['DB_NAME']
        self.exec_db_collection = cfg['EXEC_DB_COLLECTION']

        self.docker_host = cfg['DOCKER_HOST']
        self.docker_storage_secret = cfg['DOCKER_STORAGE_SECRET']
        self.docker_benchsuite_image = cfg['DOCKER_BENCHSUITE_IMAGE']

        self.docker_global_env = cfg['DOCKER_GLOBAL_ENV']
        self.docker_global_tags = cfg['DOCKER_GLOBAL_TAGS']
        self.docker_additional_opts = cfg['DOCKER_ADDITIONAL_OPTS']

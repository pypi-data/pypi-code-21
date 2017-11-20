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

import time

import datetime
import docker
import pytz
from docker.types import SecretReference, RestartPolicy

from benchsuite.scheduler.config import BenchsuiteSchedulerConfig
from benchsuite.scheduler.schedules import BenchmarkingScheduleConfig

logger = logging.getLogger(__name__)


class BenchsuiteInstance(object):

    def __init__(self, docker_service):
        self.id = docker_service.name
        self.docker_service_id = docker_service.id
        self.docker_container_id = docker_service.tasks()[0]['Status']['ContainerStatus']['ContainerID']
        self.status = docker_service.tasks()[0]['Status']['State']

        try:
            self.created = datetime.datetime.strptime(docker_service.tasks()[0]['CreatedAt'][:19], '%Y-%m-%dT%H:%M:%S')
            self.created = self.created.replace(tzinfo=pytz.utc)  # docker api returns dates in UTC
        except:
            logger.error('error parsing data: ', docker_service.tasks()[0]['CreatedAt'][:19])
            pass

        self.schedule_id = docker_service.attrs['Spec']['Labels']['benchsuite.schedule_id']
        self.username = docker_service.attrs['Spec']['Labels']['benchsuite.username']



class DockerManager(object):
    """
    Wraps the a Docker Swarm and provides methods to manage the Benchsuite
    containers
    """

    def __init__(self, config: BenchsuiteSchedulerConfig):

        self.__client = docker.DockerClient(config.docker_host)
        self._storage_secret_ref = self.__get_secret_ref(config.docker_storage_secret)
        self._global_tags = config.docker_global_tags or []
        self._global_env = config.docker_global_env or {}
        self._global_opts = config.docker_additional_opts or []
        self._benchsuite_multiexec_image = config.docker_benchsuite_image

    def create_benchsuite_multiexec_instance(self, schedule: BenchmarkingScheduleConfig):
        provider_secret_ref = self.__get_secret_ref(schedule.provider_config_secret)
        restartCond = RestartPolicy(condition='none')

        args = [
            '--storage-config', '/run/secrets/' + self._storage_secret_ref['SecretName'],
            '--provider', '/run/secrets/' + provider_secret_ref['SecretName'],
            '--failonerror',
            '--user', schedule.username
        ]

        for t in schedule.tags:
            args.extend(['--tag', t])

        args.extend(self._global_opts)
        args.extend(self._global_opts)
        args.extend(schedule.additional_opts or [])
        args.extend(schedule.tests)

        final_env = dict(self._global_env)
        final_env.update(schedule.env)
        env_list = ['{0}={1}'.format(k,v) for k,v in final_env.items()]

        name = schedule.id + '_' + schedule.username
        labels = {
            'benchsuite.source': 'benchsuite-scheduler',
            'benchsuite.schedule_id': schedule.id,
            'benchsuite.username': schedule.username}

        service = self.__client.services.create(
            self._benchsuite_multiexec_image,
            secrets=[self._storage_secret_ref, provider_secret_ref],
            args=args,
            env=env_list,
            restart_policy = restartCond,
            labels=labels,
            name=name
        )

        self.__wait_instance_ready(service)

        return BenchsuiteInstance(service)


    def __wait_instance_ready(self, service):
        retry = 10
        cont_id = None
        while retry and not cont_id:
            service.reload()
            if len(service.tasks()) > 0:
                task = service.tasks()[0]
                if 'ContainerID' in task['Status']['ContainerStatus']:
                    cont_id = task['Status']['ContainerStatus']['ContainerID']
                    break

            retry -= 1
            logger.debug('Container ID not ready yet. Retrying in 10 seconds')
            time.sleep(10)

        if not cont_id:
            raise Exception('Failed to retrieve the container id after 100 seconds')


    def wait(self, instance):
        cont = self.__client.containers.get(instance.docker_container_id)
        retval = cont.wait()
        log = cont.logs().decode()
        return retval, log

    def remove_instance(self, instance):
        self.__client.services.get(instance.docker_service_id).remove()

    def list(self):
        services = self.__client.services.list(filters={'label': 'benchsuite.source=benchsuite-scheduler'})

        return [BenchsuiteInstance(s) for s in services]

    def stop_service(self):
        raise NotImplementedError()

    def stop_all(self):
        raise NotImplementedError()

    def __get_secret_ref(self,name_or_id):
        for s in self.__client.secrets.list():
            if s.id == name_or_id or s.name == name_or_id:
                return SecretReference(s.id, s.name)

        return None

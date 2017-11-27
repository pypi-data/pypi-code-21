import docker
import logging
import os
import subprocess
import sys

import portinus

log = logging.getLogger(__name__)


def run(name):
    service = portinus.Service(name)
    monitored_compose_containers = get_monitored_compose_containers(name)

    for container in monitored_compose_containers:
        log.debug("Checking container {container_id}, name: '{name}'".format(container_id=container.id, name=container.attrs['Name']))
        if not check_container_health(container):
            log.info("Container {container_id}, name: '{container_name}'. Restarting stack for {name}".format(container_id=container.id, container_name=container.attrs['Name'], name=name))
            print("Container '{container_name} found unhealthy. Restarting the {name} stack...".format(container_name=container.attrs['Name'], name=name))
            service.restart()
            return False
    print("No unhealthy containers found")
    return True


def check_container_health(container):
    status = container.attrs["State"]["Health"]["Status"]
    return status != "unhealthy"


def get_monitored_compose_containers(name):
    compose_container_ids = get_compose_container_ids(name)
    monitored_containers = get_monitored_containers()
    monitored_compose_containers = []

    for container_id in compose_container_ids:
        valid_container = next((x for x in monitored_containers if x.id == container_id), None)
        if valid_container: monitored_compose_containers.append(valid_container)

    log.debug("Found {count} monitored containers from docker-compose".format(count=len(monitored_compose_containers)))
    return monitored_compose_containers


def get_compose_container_ids(name):
    compose_source = portinus.ComposeSource(name)
    service_script = compose_source.service_script

    compose_output = subprocess.check_output([service_script, "ps", "-q"], stderr=subprocess.DEVNULL).decode("utf-8")
    container_list = compose_output.split("\n")

    filtered_container_list = list((x for x in container_list if x))

    log.debug("Found {count} total containers from docker-compose".format(count=len(filtered_container_list)))
    return filtered_container_list


def get_monitored_containers():
    client = docker.from_env()

    all_containers = client.containers.list()

    monitored_containers = []

    for container in all_containers:
        if 'Health' in container.attrs['State']:
            monitored_containers.append(container)

    log.debug("Found {count} monitored containers from docker".format(count=len(monitored_containers)))
    return monitored_containers

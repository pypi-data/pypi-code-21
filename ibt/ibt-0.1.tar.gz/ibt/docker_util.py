###############################################################################
#
# IBT: Isolated Build Tool
# Copyright (C) 2016, Richard Cook. All rights reserved.
#
# Simple wrappers around Docker etc. for fully isolated build environments
#
###############################################################################

from __future__ import print_function
import subprocess32

from ibt.container_util import check_process_in_container
from ibt.util import call_process, check_process

def docker_installed():
    try:
        return call_process(["docker", "--version"], timeout=1)
    except (OSError, subprocess32.TimeoutExpired):
        return False

def docker_image_exists(image_id):
    return call_process(["docker", "inspect", image_id])

def docker_image_build(image_id, context_dir):
    if docker_image_exists(image_id):
        print("Docker image {} already built".format(image_id))
    else:
        print("Building Docker image {}".format(image_id))
        check_process(["docker", "build", "-t", image_id, context_dir])

def docker_image_remove(image_id):
    if docker_image_exists(image_id):
        print("Destroying Docker image {}".format(image_id))
        check_process(["docker", "rmi", image_id])
    else:
        print("No Docker image {} to destroy".format(image_id))

def docker_run(ctx, project, args, container_run_path):
    check_process_in_container(ctx, project, args, None, ["/bin/sh", container_run_path])

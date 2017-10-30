###############################################################################
#
# IBT: Isolated Build Tool
# Copyright (C) 2016, Richard Cook. All rights reserved.
#
# Simple wrappers around Docker etc. for fully isolated build environments
#
###############################################################################

from __future__ import print_function
import os
import re
import subprocess

from ibt.tracing import trace_command
from ibt.util import ensure_mount_sources

def _expand(env_vars, value):
    def _replace(m):
        key = m.group(1)
        replacement = env_vars.get(key)
        return m.group(0) if replacement is None else replacement

    return re.sub('\$([A-Za-z_][A-Za-z_0-9]*)', _replace, value)

def _build_command(ctx, project, command_args, subcommand):
    container_project_dir = project.settings.get("container-project-dir", project.default_container_project_dir)

    rel_dir = os.path.relpath(ctx.working_dir, project.root_dir)
    container_working_dir = os.path.join(container_project_dir, rel_dir)

    additional_args = []

    ports = {}

    ports_setting = project.settings.get("ports", None)
    if ports_setting is not None:
        for key in ports_setting:
            host_port = key
            container_port = ports_setting[key]
            if host_port in ports:
                raise RuntimeError("Duplicate host port {}".format(host_port))
            ports[host_port] = container_port

    volumes = {
        project.root_dir: container_project_dir,
        project.dot_dir: project.container_dot_dir
    }

    volumes_setting = project.settings.get("volumes", None)
    if volumes_setting is not None:
        for key in volumes_setting:
            local_dir = project.resolve_local_path(key)
            container_dir = volumes_setting[key]
            if local_dir in volumes:
                raise RuntimeError("Duplicate volume {}".format(local_dir))
            volumes[local_dir] = container_dir

    _, _, _, user_name = ctx.user_info()

    env_vars = {
        "IBTPROJECTDIR": container_project_dir,
        "IBTUSER": user_name,
        "USER": user_name
    }

    env_vars_setting = project.settings.get("env_vars", None)
    if env_vars_setting is not None:
        for key in env_vars_setting:
            env_vars[key] = env_vars_setting[key]

    command = [
        "docker",
        "run",
        "--security-opt",
        "seccomp:unconfined",
        "-w",
        container_working_dir,
        "-u",
        user_name,
        "--rm"
    ] + \
        sum([["-p", "{}:{}".format(key, ports[key])] for key in ports], []) + \
        sum([["--volume", "{}:{}".format(key, _expand(env_vars, volumes[key]))] for key in volumes], []) + \
        sum([["--env", "{}={}".format(key, env_vars[key])] for key in env_vars], []) + \
        additional_args + \
        ([] if command_args is None else command_args) + \
        [project.image_id] + \
        ([] if subcommand is None else subcommand)

    return command, volumes

def check_process_in_container(ctx, project, args, command_args=None, subcommand=None):
    command, volumes = _build_command(ctx, project, command_args, subcommand)
    trace_command(args, command)
    with ensure_mount_sources(volumes.keys()):
        subprocess.check_call(command)

def call_process_in_container(ctx, project, args, command_args=None, subcommand=None):
    command, volumes = _build_command(ctx, project, command_args, subcommand)
    trace_command(args, command)
    with ensure_mount_sources(volumes.keys()):
        return subprocess.call(command)

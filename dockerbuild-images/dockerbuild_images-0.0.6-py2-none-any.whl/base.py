# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import subprocess


DOCKERFILE_NAME = 'Dockerfile'
DOCKER_COMMAND = os.environ.get('DOCKERBUILD_DOCKER_COMMAND', 'docker')


def docker_build_command(dockerfile_name, image_name):
    return [
        DOCKER_COMMAND, 'build', '-f', dockerfile_name, '-t', image_name, '.'
    ]


def handle_directory(relative_root, files, config_adapter, dockerfile_name=DOCKERFILE_NAME):
    for fname in files:
        fname = fname.decode('utf-8')
        if dockerfile_name not in fname:
            continue

        parts = filter(bool, [
            p.strip('_') for p in fname.split(dockerfile_name, 1)
        ])
        parts = parts or [os.path.basename(relative_root)]
        image_name = parts[0]
        root_absolute = os.path.join(os.getcwd(), relative_root)
        root_absolute = os.path.abspath(root_absolute)
        command = docker_build_command(fname, image_name)

        exclude = False
        if not config_adapter:
            yield (root_absolute, fname, image_name, command, exclude)
            continue

        result = config_adapter.adapt(root_absolute, fname, image_name)
        if not result:
            exclude = True
            yield (root_absolute, fname, image_name, command, exclude)
            continue

        root_absolute, fname, image_name = result
        command = docker_build_command(fname, image_name)
        exclude = False
        yield (root_absolute, fname, image_name, command, exclude)


def find_docker_files(path, config_adapter, paths_provided, dockerfile_name=DOCKERFILE_NAME):
    if paths_provided:
        for root, dirs, files in os.walk(path):
            if '.git' in root:
                continue
            for item in handle_directory(root, files, config_adapter, dockerfile_name):
                yield item
        return  # END !

    files = [
        os.path.join(path, fname)
        for fname in os.listdir(path)
    ]
    for item in handle_directory(path, files, config_adapter, dockerfile_name):
        yield item


def get_base_image_name(dockerfile_path):
    # reads "FROM" image from the given dockerfile
    with open(dockerfile_path, 'r') as fd:
        for line in fd.readlines():
            if line.startswith('FROM '):
                splited = [item.strip('\n') for item in line.split('FROM ') if item.strip('\n')]
                dependency_image = splited[-1]
                return dependency_image


def build(root, docker_filename, image_name, command, dry=False):
    curdir = os.getcwd()
    try:
        os.chdir(root)
        if not dry:
            subprocess.check_call(command)
        return True
    except subprocess.CalledProcessError:
        return False
    finally:
        os.chdir(curdir)

# -*- coding: utf-8 -*-
import os
import time
import datetime

import click

from .base import find_docker_files, build, get_base_image_name
from . import dependency
from . import config_reader


def log(*args, **kwargs):
    return click.secho(*args, **kwargs)


def log_green(*args, **kwargs):
    kwargs.update(fg='green', bold=True)
    return click.secho(*args, **kwargs)


def err(*args, **kwargs):
    kwargs.update(fg='red', bold=True)
    return click.secho(*args, **kwargs)


@click.command()
@click.option('--no-verbose', is_flag=True)
@click.option('--dry', is_flag=True, help='Show only what script will do')
@click.option('--sleep', default=2, help='Wait of some seconds before building found Dockerfile')
def main(no_verbose, dry, sleep):
    sleep = 0 if dry else sleep

    dockerbuild_filepath = os.path.abspath(
        os.path.join(os.getcwd(), 'dockerbuild.yml')
    )
    if not os.path.exists(dockerbuild_filepath):
        raise click.UsageError('Configuration file "dockerbuild.yml" does not exists.')

    try:
        adapter = config_reader.read(dockerbuild_filepath)
    except config_reader.ValidationError as e:
        raise click.UsageError(e.message)

    paths = [
        item['path'] for item in adapter.images_recursive if item.get('path')
    ]
    paths_provided = bool(paths)
    paths = paths or ['./']

    # TODO: CLEAN ME UP
    seen = set()
    declared = set()
    edges = []
    images_params = {}
    for path in paths:
        for root, docker_filename, image_name, command, exclude in find_docker_files(path, adapter, paths_provided):
            seen_item = (root, docker_filename, image_name)
            if seen_item in seen:
                continue
            declared.add(image_name)
            base_image = get_base_image_name(os.path.join(root, docker_filename))
            edges.append((image_name, base_image))
            images_params[image_name] = (
                root, docker_filename, image_name, command, exclude
            )

    building_order = dependency.resolve(edges, relevant_nodes=declared)

    results = []
    for image_name in building_order:
        root, docker_filename, image_name, command, exclude = images_params[image_name]

        if not no_verbose:
            log(u'*' * 80)
            log(u'   Dockerfile | %s' % os.path.abspath(os.path.join(root, docker_filename)))
            log(u'   Image name | %s' % image_name)
            if not exclude:
                log(u'   Command    | %s' % ' '.join(command))
            else:
                err(u'   EXLUDING   | Excluded by config file')
            if not dry:
                log(u'*' * 80)
                log(u'')

        if exclude:
            continue

        if sleep:
            time.sleep(sleep)

        start = datetime.datetime.now()
        was_ok = build(root, docker_filename, image_name, command, dry=dry)
        took = datetime.datetime.now() - start

        if not dry:
            log('')  # let's do one extra new-line after

        results.append(
            (root, docker_filename, image_name, command, was_ok, took)
        )
        if not was_ok:
            err('    %s' % ('*' * 80))
            err('    SOMETHING WENT WRONG WITH BUILD !!! ')
            err('    %s' % ('*' * 80))
            err('')

    if dry:
        return

    log('\n')
    log('=' * 80)
    for root, docker_filename, image_name, command, was_ok, took in results:
        log(' - %s' % (os.path.abspath(os.path.join(root, docker_filename))))
        if was_ok:
            log_green('    OK | took: %s' % (took))
        else:
            err('    ERROR | You might want to go to the directory and check things out')
            err('          | $> cd %s' % root)
            err('          | $> %s' % ' '.join(command))

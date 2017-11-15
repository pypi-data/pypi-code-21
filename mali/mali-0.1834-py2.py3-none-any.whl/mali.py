#!/usr/bin/env python
# coding=utf-8
import click
import sys
import logging
from self_update.sdk_version import get_version, get_keywords


class Expando(object):
    pass


package = 'mali'


@click.group()
@click.option('--outputFormat', '-o', type=click.Choice(['tables', 'json']), default='tables', required=False)
@click.option('--configPrefix', '-cp', envvar='CONFIG_PREFIX', required=False)
@click.option('--configFile', '-cf', envvar='CONFIG_FILE', required=False)
@click.pass_context
def cli(ctx, outputformat, configprefix, configfile):
    from mali_commands.config import Config

    ctx.obj = Expando()

    from mali_commands.commons import handle_api

    config = Config(configprefix, configfile)

    ctx.obj.config = config
    ctx.obj.handle_api = handle_api

    ctx.obj.api_host = config.api_host
    ctx.obj.host = config.host
    ctx.obj.client_id = config.client_id
    ctx.obj.refresh_token = config.refresh_token

    ctx.obj.auth0 = config.auth0
    ctx.obj.output_format = outputformat

    ctx.obj.refresh_token = config.refresh_token
    ctx.obj.id_token = config.id_token


@cli.command('version')
def version():
    current_version = get_version(package)

    click.echo('%s %s' % (package, current_version))


# noinspection PyBroadException
def update_sdk(latest_version, user_path, throw_exception):
    from self_update.pip_util import pip_install, get_pip_server

    keywords = get_keywords(package) or []

    require_package = '%s==%s' % (package, latest_version)
    p, args = pip_install(get_pip_server(keywords), require_package, user_path)

    if p is None:
        return False

    try:
        std_output, std_err = p.communicate()
    except Exception:
        if throw_exception:
            raise

        logging.exception("%s failed", " ".join(args))
        return False

    rc = p.returncode

    if rc != 0:
        logging.error('%s failed to upgrade to latest version (%s)', package, latest_version)
        logging.error("failed to run %s (%s)\n%s\n%s", " ".join(args), rc, std_err, std_output)
        return False

    logging.info('%s updated to latest version (%s)', package, latest_version)

    return True


def self_update(throw_exception=False):
    from self_update.pip_util import get_latest_pip_version

    current_version = get_version(package)
    keywords = get_keywords(package) or []

    if current_version is None:
        return

    latest_version = get_latest_pip_version(package, keywords, throw_exception=throw_exception)

    if latest_version is None:
        return

    if current_version == latest_version:
        return

    running_under_virtualenv = getattr(sys, 'real_prefix', None) is not None

    if not running_under_virtualenv:
        logging.info('updating %s to version %s in user path', package, latest_version)

    return update_sdk(latest_version, user_path=not running_under_virtualenv, throw_exception=throw_exception)


def add_commands():
    from mali_commands import auth_commands, projects_commands, orgs_commands, experiments_commands, runcode_commands, \
        models_commands, data_commands

    cli.add_command(auth_commands)
    cli.add_command(projects_commands)
    cli.add_command(orgs_commands)
    cli.add_command(experiments_commands)
    cli.add_command(runcode_commands)
    cli.add_command(models_commands)
    cli.add_command(data_commands)


def main():
    self_update()
    add_commands()
    cli()


if __name__ == "__main__":
    main()

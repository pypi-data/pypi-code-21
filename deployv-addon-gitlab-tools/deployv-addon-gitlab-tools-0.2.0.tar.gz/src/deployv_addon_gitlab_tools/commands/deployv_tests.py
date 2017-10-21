# coding: utf-8

from deployv_addon_gitlab_tools.common import check_env_vars
from docker import errors, APIClient as Client
from os import environ
import re
import subprocess
import shlex
import sys
import psycopg2
import shutil
import time
import click
import logging


logger = logging.getLogger('deployv.' + __name__)  # pylint: disable=C0103
_cli = Client()


def generate_image_name(name):
    """ Generate the base image name usig the ref name but cleaning it before,
    ATM only removes "." and "#" from the title to avoid issues with docker naming
    convention """
    res = re.sub(r'[\.#\$\=\+\;\>\,\<,\&\%]', '', name)
    res = re.sub(r'-_', '_', res)
    return res.lower()


def postgres_container(base_name):
    return 'postgres{0}_{1}'.format(base_name, environ['CI_PIPELINE_ID'])


def configure_postgres(base_name, postgres_image):
    logger.info('Updating postgres')
    cmd = ('apk add "postgresql-dev@edge>={ver}" "postgresql-client@edge>={ver}"'
           ' "postgresql@edge>={ver}"'.format(ver=environ.get('PSQL_VERSION', '9.6')))
    subprocess.check_call(shlex.split('apk update'))
    subprocess.check_call(shlex.split(cmd))
    name = postgres_container(base_name)
    logger.info('Pulling the postgres image')
    _cli.pull(postgres_image)
    logger.info('Creating container %s', name)
    container = _cli.create_container(name=name,
                                      image='postgres:9.6',
                                      environment={'POSTGRES_PASSWORD': 'postgres'})
    _cli.start(container=container.get('Id'))
    time.sleep(20)
    container_info = _cli.inspect_container(container.get('Id'))
    postgres_host = container_info.get('NetworkSettings').get('IPAddress')
    environ['PGHOST'] = postgres_host
    environ['PGPASSWORD'] = 'postgres'


def configure_postgres_user():
    logger.info('Creating user docker')
    retry = 0
    while True:
        try:
            with psycopg2.connect(user='postgres') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "create user docker password 'docker' createdb;"
                )
                break
        except psycopg2.OperationalError as error:
            if 'could not connect to server' in error and retry <= 3:
                retry += 1
                logger.error('Failed to connect to the database, retrying %s', retry)
                time.sleep(4)
            else:
                logger.error(error)
                return False
    environ['PGPASSWORD'] = 'docker'
    environ['PGUSER'] = 'docker'
    return True


def run_tests():
    logger.info('Copying files required for the tests')
    shutil.copy('tests/files/config.json.travis', 'tests/files/config.json')
    logger.info('Running tests')
    try:
        subprocess.check_call(shlex.split('coverage run setup.py test'))
        subprocess.check_call(shlex.split('coverage report -m'))
        subprocess.check_call(shlex.split('tox -e doc'))
    except subprocess.CalledProcessError:
        return False
    return True


def cleanup(base_name):
    containers = _cli.containers(all=True)
    for container in containers:
        for name in container.get('Names'):
            if base_name in name:
                try:
                    _cli.remove_container(container, force=True)
                except errors.NotFound:
                    logger.error('Container already deleted')


@click.command()
@click.option('--ci_pipeline_id', default=environ.get('CI_PIPELINE_ID'),
              help=("The unique id of the current pipeline that GitLab CI"
                    " uses internally. Env var: CI_PIPELINE_ID."))
@click.option('--ci_commit_ref_name', default=environ.get('CI_COMMIT_REF_NAME'),
              help=("The branch or tag name for which project is built."
                    " Env var: CI_COMMIT_REF_NAME."))
@click.option('--ci_job_id', default=environ.get('CI_JOB_ID'),
              help=("The unique id of the current job that GitLab CI uses internally."
                    " Env var: CI_JOB_ID."))
def deployv_tests(**kwargs):
    check_env_vars(**kwargs)
    base_name = generate_image_name('{0}_{1}'.format(
        kwargs.get('ci_commit_ref_name'), kwargs.get('ci_job_id')))
    postgres_image = 'postgres:{0}'.format(environ.get('PSQL_VERSION', '9.6'))
    cleanup(base_name)
    configure_postgres(base_name, postgres_image)
    res = configure_postgres_user()
    if not res:
        cleanup(base_name)
        sys.exit(1)
    res = run_tests()
    cleanup(base_name)
    if not res:
        sys.exit(1)
    sys.exit(0)

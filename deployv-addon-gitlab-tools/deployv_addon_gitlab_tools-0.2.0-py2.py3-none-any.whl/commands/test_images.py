# coding: utf-8

from deployv_addon_gitlab_tools.common import check_env_vars
from deployv.helpers import utils
from docker import errors, APIClient as Client
from os import environ
import re
import subprocess
import time
import shlex
import sys
import click
import logging
import json


logger = logging.getLogger('deployv.' + __name__)  # pylint: disable=C0103
_cli = Client()


def generate_image_name(name):
    """ Generate the base image name usig the ref name but cleaning it before,
    ATM only removes "." and "#" from the title to avoid issues with docker naming
    convention """
    res = re.sub(r'[\.#\$\=\+\;\>\,\<,\&\%]', '', name)
    res = re.sub(r'-_', '_', res)
    return res.lower()


def build_image():
    logger.info('Building image')
    cmd = ('deployvcmd build -b {branch} -u {url} -v {version} -i {image} -O {repo}#{odoo_branch} -T {tag}'
           .format(branch=environ['CI_COMMIT_REF_NAME'], url=environ['CI_REPOSITORY_URL'], repo=environ['ODOO_REPO'],
                   odoo_branch=environ['ODOO_BRANCH'], version=environ['VERSION'], image=environ['BASE_IMAGE'],
                   tag=environ['_INSTANCE_IMAGE']))
    subprocess.check_call(shlex.split(cmd))


def pull_images():
    """ Pulls images needed for the build and test process """
    images = [environ['BASE_IMAGE'],
              environ['_POSTGRES_IMAGE']]
    for image in images:
        logger.info('Pulling: %s', image)
        _cli.pull(image)
    return images


def postgres_container():
    return 'postgres{0}_{1}'.format(environ['_BASE_NAME'], environ['CI_PIPELINE_ID'])


def clean_containers():
    """ Cleans any running container related to the same build to avoid any conflicts """
    containers = _cli.containers(all=True, filters={'name': environ['_BASE_NAME']})
    for container in containers:
        logger.info('Removing container %s', container.get('Name', container.get('Names')[0]))
        _cli.remove_container(container['Id'], force=True)
    logger.info('Removing image %s', environ['_INSTANCE_IMAGE'])
    try:
        _cli.remove_image(environ['_INSTANCE_IMAGE'])
    except errors.APIError as error:
        if 'No such image' in error.explanation:
            pass
    logger.info('Image %s deleted', environ['_INSTANCE_IMAGE'])


def start_postgres():
    logger.info('Starting container %s', postgres_container())
    container = _cli.create_container(image=environ['_POSTGRES_IMAGE'],
                                      name=postgres_container(),
                                      environment={'POSTGRES_PASSWORD': 'postgres'})
    _cli.start(container=container.get('Id'))
    logger.info(container)


def create_postgres_user():
    cmd = "psql -c \"create user odoo with password 'odoo' createdb\""
    res = exec_cmd(postgres_container(), cmd, 'postgres')
    return res


def start_instance():
    env = {
        "DB_USER": "odoo",
        "DB_PASSWORD": "odoo",
        "DB_HOST": postgres_container(),
        "ODOO_CONFIG_FILE": "/home/odoo/.openerp_serverrc"
    }
    for env_var in ['COUNTRY', 'LANGUAGE']:
        env.update({env_var: environ.get(env_var, "")})
    links = {
        postgres_container(): postgres_container()
    }
    host_config = _cli.create_host_config(links=links)
    logger.info('Starting container %s', environ['_INSTANCE_IMAGE'])
    logger.debug('Env vars %s', json.dumps(env, sort_keys=True, indent=4))
    container = _cli.create_container(image=environ['_INSTANCE_IMAGE'],
                                      name=environ['_INSTANCE_IMAGE'],
                                      environment=env,
                                      host_config=host_config)
    _cli.start(container=container.get('Id'))
    logger.info(container)


def install_module():
    module = environ['INSTALL']
    extra = ''
    if environ.get('LANGUAGE'):
        extra += ' --load-language={lang}'.format(lang=environ.get('LANGUAGE'))
    install_wdemo = (
        "/home/odoo/instance/odoo/odoo-bin -d wdemo -i {mod}"
        "{extra} --stop-after-init".format(mod=module, extra=extra)
    )
    install_wodemo = (
        "/home/odoo/instance/odoo/odoo-bin -d wodemo -i {mod}"
        "{extra} --stop-after-init --without-demo=all".format(mod=module, extra=extra)
    )
    logger.info('Verifying supervisorctl')
    is_running()
    logger.info('Stopping odoo')
    exec_cmd(environ['_INSTANCE_IMAGE'], 'supervisorctl stop odoo')
    logger.info('\nInstalling %s with demo', module)
    logger.debug('Command : %s', install_wdemo)
    wdemo_res = exec_cmd(environ['_INSTANCE_IMAGE'], install_wdemo, 'odoo', stream=True)
    wdemo_log = resume_log(wdemo_res)
    logger.info('\nInstalling %s without demo', module)
    logger.debug('Command : %s', install_wodemo)
    wodemo_res = exec_cmd(environ['_INSTANCE_IMAGE'], install_wodemo, 'odoo', stream=True)
    wodemo_log = resume_log(wodemo_res)
    show_log(wdemo_log[1], 'Installation with demo')
    show_log(wodemo_log[1], 'Installation without demo')
    if not wdemo_log[0] or not wodemo_log[0]:
        return False
    return True


def exec_cmd(container, cmd, user=None, stream=False):
    lines = []
    container_id = _cli.inspect_container(container).get('Id')
    logger.debug('Executing command "{cmd}" in container "{con}".'.format(cmd=cmd, con=container))
    try:
        exec_id = _cli.exec_create(container_id, cmd, user=user)
    except errors.APIError as error:
        logger.error('Error: %s', error.explanation)
        raise
    res = _cli.exec_start(exec_id.get('Id'), stream=stream)
    if stream:
        for line in res:
            line = utils.decode(line)
            logger.info(line.strip('\n'))
            lines.append(line)
        return lines
    return utils.decode(res)


def show_log(log, title):
    logger.info('\n%s', title)
    logger.info('='*20)
    logger.info('+-- Critical errors %s', len(log.get('critical')))
    logger.info('+-- Errors %s', len(log.get('errors')))
    logger.info('+-- Import errors %s', len(log.get('import_errors')))
    logger.info('+-- Warnings %s', len(log.get('warnings')))
    logger.info('+-- Translation Warnings %s', len(log.get('warnings_trans')))
    logger.info('='*20)


def resume_log(log_lines):
    """Gets the log lines from -u (modules or all) and parse them to get the totals
    according to the filters dict

    :param log_lines: each element of the list is a log line
    :return: dict with key filters as keys and a list with all matched lines
    """
    def critical(line):
        criteria = re.compile(r'.*\d\sCRITICAL\s.*')
        return criteria.match(line)

    def errors(line):
        criteria = re.compile(r'.*\d\sERROR\s.*')
        return criteria.match(line)

    def warnings_trans(line):
        criteria = re.compile(
            r'.*\d\sWARNING\s.*no translation for language.*')
        return criteria.match(line)

    def import_errors(line):
        criteria = re.compile(r'^ImportError.*')
        return criteria.match(line)

    def warnings(line):
        criteria = re.compile(r'.*\d\sWARNING\s.*')
        return criteria.match(line) and 'no translation for language' not in line

    filters = {
        'critical': critical,
        'errors': errors,
        'warnings': warnings,
        'warnings_trans': warnings_trans,
        'import_errors': import_errors
    }
    success = True
    res = {name: [] for name in filters}
    for line in log_lines:
        stripped_line = line.strip()
        for name, criteria in filters.items():
            if criteria(stripped_line):
                if name in ['critical', 'error']:
                    success = False
                elif name == 'warnings' and 'Deprecated' in stripped_line:
                    success = False
                res.get(name).append(stripped_line)
                break
    return (success, res)


def is_running():
    retry = True
    retries = 0
    while retry and retries <= 10:
        try:
            res = exec_cmd(environ['_INSTANCE_IMAGE'], 'supervisorctl status odoo')
        except errors.APIError:
            retries += 1
            logger.warn('Container error, retrying %s', retries)
            time.sleep(5)
            continue
        logger.info('is_running: %s', res.strip())
        if 'STARTING' in res or 'STOPPING' in res:
            logger.warn('The Odoo process is in an intermediate state, retrying')
            time.sleep(5)
        elif 'RUNNING' in res:
            return True
        elif 'STOPPED' in res:
            return False
        elif res == '' or 'no such file' in res:
            retries += 1
            logger.warn('Supervisor returned empty or not running yet, retrying %s', retries)
            time.sleep(5)
        else:
            retries += 1
            logger.warn('Unknown state: %s', res)
            time.sleep(5)


@click.command()
@click.option('--ci_commit_ref_name', default=environ.get('CI_COMMIT_REF_NAME'),
              help=("The branch or tag name for which project is built."
                    " Env var: CI_COMMIT_REF_NAME."))
@click.option('--ci_pipeline_id', default=environ.get('CI_PIPELINE_ID'),
              help=("The unique id of the current pipeline that GitLab CI"
                    " uses internally. Env var: CI_PIPELINE_ID."))
@click.option('--ci_repository_url', default=environ.get('CI_REPOSITORY_URL'),
              help=("The URL to clone the Git repository."
                    " Env var: CI_REPOSITORY_URL."))
@click.option('--base_image', default=environ.get('BASE_IMAGE'),
              help=("Env var: BASE_IMAGE."))
@click.option('--odoo_repo', default=environ.get('ODOO_REPO'),
              help=("Env var: ODOO_REPO."))
@click.option('--odoo_branch', default=environ.get('ODOO_BRANCH'),
              help=("Env var: ODOO_BRANCH."))
@click.option('--version', default=environ.get('VERSION'),
              help=("Env var: VERSION."))
@click.option('--install', default=environ.get('INSTALL'),
              help=("Env var: INSTALL."))
@click.option('--ci_job_id', default=environ.get('CI_JOB_ID'),
              help=("The unique id of the current job that GitLab CI uses internally."
                    " Env var: CI_JOB_ID."))
def test_images(**kwargs):
    check_env_vars(**kwargs)
    base_name = generate_image_name('{0}_{1}'.format(
        kwargs.get('ci_commit_ref_name'), kwargs.get('ci_job_id')))
    postgres_image = 'postgres:{0}'.format(environ.get('PSQL_VERSION', '9.5'))
    instance_image = generate_image_name('instance{0}_{1}'.format(
        base_name, kwargs.get('ci_pipeline_id')))
    environ.update({
        '_BASE_NAME': base_name,
        '_POSTGRES_IMAGE': postgres_image,
        '_INSTANCE_IMAGE': instance_image,
    })
    clean_containers()
    pull_images()
    start_postgres()
    build_image()
    create_postgres_user()
    start_instance()
    res = install_module()
    clean_containers()
    if not res:
        sys.exit(1)
    sys.exit(0)


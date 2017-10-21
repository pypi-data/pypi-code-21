# coding: utf-8

from deployv_addon_gitlab_tools.common import check_env_vars
from deployv.helpers import utils
from docker import APIClient as Client
from os import environ
import subprocess
import shlex
import sys
import click
import logging
import json


_logger = logging.getLogger('deployv.' + __name__)
_cli = Client(timeout=600)


def build_image():
    format_values = {
        'url': environ['CI_REPOSITORY_URL'],
        'version': environ['CI_COMMIT_REF_NAME'],
        'base': environ['BASE_IMAGE'],
        'odoo_repo': environ['ODOO_REPO'],
        'odoo_branch': environ['ODOO_BRANCH'],
        'name': environ['_IMAGE_NAME'],
    }
    _logger.info('Bulding image %s', environ['_IMAGE_NAME'])
    cmd = (
        'deployvcmd build -u {url} -v {version} -i {base} -O {odoo_repo}#{odoo_branch} -T {name}'
        .format(**format_values)
    )
    subprocess.check_call(shlex.split(cmd))


def push_image():
    for tag in ['latest', environ['_IMAGE_TAG']]:
        _logger.info('Pushing image %s to %s:%s', environ['_IMAGE_NAME'], environ['_IMAGE_REPO'], tag)
        _cli.tag(environ['_IMAGE_NAME'], environ['_IMAGE_REPO'], tag=tag)
        for result in _cli.push(environ['_IMAGE_REPO'], tag=tag, stream=True):
            result = json.loads(utils.decode(result))
            if result.get('error'):
                _logger.error(result.get('error'))
                sys.exit(1)


@click.command()
@click.option('--ci_project_name', default=environ.get('CI_PROJECT_NAME'),
              help=("The project name that is currently being built."
                    " Env var: CI_PROJECT_NAME."))
@click.option('--CI_COMMIT_SHA', default=environ.get('CI_COMMIT_SHA'),
              help=("The commit revision for which project is built."
                    " Env var: CI_COMMIT_SHA."))
@click.option('--CI_COMMIT_REF_NAME', default=environ.get('CI_COMMIT_REF_NAME'),
              help=("The branch or tag name for which project is built."
                    " Env var: CI_COMMIT_REF_NAME."))
@click.option('--CI_REPOSITORY_URL', default=environ.get('CI_REPOSITORY_URL'),
              help=("The URL to clone the Git repository."
                    " Env var: CI_REPOSITORY_URL."))
@click.option('--base_image', default=environ.get('BASE_IMAGE'),
              help=("Env var: BASE_IMAGE."))
@click.option('--odoo_repo', default=environ.get('ODOO_REPO'),
              help=("Env var: ODOO_REPO."))
@click.option('--odoo_branch', default=environ.get('ODOO_BRANCH'),
              help=("Env var: ODOO_BRANCH."))
@click.option('--image_repo_url', default=environ.get('IMAGE_REPO_URL', "quay.io/vauxoo"),
              help=("The URL where the image repository is located."
                    " Env var: IMAGE_REPO_URL."))
def upload_image(**kwargs):
    check_env_vars(**kwargs)
    customer_names = environ.get('CUSTOMER', environ.get('CI_PROJECT_NAME'))
    version_tag = environ.get('CI_COMMIT_REF_NAME').replace('.', '')
    image_name = '{customer}_{ver}'.format(
        customer=customer_names.replace(' ', '').replace(',', '_'),
        ver=version_tag
    )
    image_tag = environ['CI_COMMIT_SHA'][:7].lower()
    environ.update({
        '_IMAGE_NAME': image_name,
        '_IMAGE_TAG': image_tag,
    })
    build_image()
    for customer_name in customer_names.split(','):
        if customer_name.strip():
            customer_img = '{customer}{ver}'.format(customer=customer_name.strip(),
                                                    ver=version_tag)
            image_repo = '{url}/{image}'.format(url=environ.get('IMAGE_REPO_URL'),
                                                image=customer_img)
            environ.update({'_IMAGE_REPO': image_repo})
            push_image()
    sys.exit(0)

# coding: utf-8

from deployv.helpers import utils
from os import path, makedirs, environ, chmod
import subprocess
import click
import logging


logger = logging.getLogger('deployv.' + __name__)  # pylint: disable=C0103
TO_SCAN = ['git.vauxoo.com',
           'github.com']


def check_ssh_folder():
    """ Check if the folder exists and create it

    :return: The full path to the .ssh folder
    """
    home_path = path.expanduser(path.join('~', '.ssh'))
    if not path.isdir(home_path):
        makedirs(home_path)
    return home_path


def add_private_key(key, folder):
    """ Generates the id_rsa file if it doesn't exits with the proper
    format and permissions

    :param key: The key content
    :param folder: The folder where the id_rsa file will be stored
    """
    ssh_file = path.join(folder, 'id_rsa')
    if path.isfile(ssh_file):
        logger.info('The id_rsa file already exists, nothing to do')
        return
    with open(ssh_file, 'w') as ssh_key:
        ssh_key.write(key)
    try:
        subprocess.check_call(['dos2unix', ssh_file])
    except subprocess.CalledProcessError:
        logger.error('You need to install dos2unix to check the key')
    chmod(ssh_file, 0o0600)


def scan_keys(folder):
    """ Performs a ssk-key scan in the list of hosts and add the keys to the
    known_hosts files

    :param folder: The folder where the file will be stored
    """
    known_hosts = path.join(folder, 'known_hosts')
    with open(known_hosts, 'a') as known_file:
        for host in TO_SCAN:
            keys = subprocess.check_output(['ssh-keyscan', host], stderr=subprocess.STDOUT)
            for line in utils.decode(keys).split('\n'):
                clean = line.strip()
                if clean:
                    known_file.write(clean + '\n')
    subprocess.check_call(['ls', '-l', folder])


@click.command()
@click.option('--private_deploy_key',
              default=environ.get('PRIVATE_DEPLOY_KEY', False),
              help="Env var: PRIVATE_DEPLOY_KEY.")
def check_keys(private_deploy_key):
    """Checks if the .ssh folder exists, creates it and add the private key
    if necessary"""
    ssh_folder = check_ssh_folder()
    if private_deploy_key:
        add_private_key(private_deploy_key, ssh_folder)
    scan_keys(ssh_folder)

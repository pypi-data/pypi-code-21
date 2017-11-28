"""
  This file contains utilities that bind the Jupyter notebook to our platform.
  It performs two functions:
  1. On startup, pull the contents of the notebook from platform to the local disk
  2. As a Jupyter post-save hook, push the contents of the notebook and a HTML preview of the same back to platform.
  3. Custom Error class for when a Notebook does not correctly initialize
"""
import civis
import logging
import os
import sys
import requests
from subprocess import check_call
from subprocess import CalledProcessError


def initialize_notebook_from_platform():
    """ This runs on startup to initialize the notebook """
    client = get_client()
    nb = client.notebooks.get(os.environ['PLATFORM_OBJECT_ID'])

    logger.info('Getting URL for notebook file')
    r = requests.get(nb.notebook_url)
    if r.status_code != 200:
        raise NotebookManagementError('Failed to pull down notebook file from S3')

    logger.info('Pulling contents of notebook file')
    with open('notebook.ipynb', 'wb') as nb_file:
        nb_file.write(r.content)
    logger.info('Notebook file ready')

    if hasattr(nb, 'requirements_url') and nb.requirements_url:
        __pull_and_load_requirements(nb.requirements_url)


def __pull_and_load_requirements(url):
    logger.info('Pulling down the requirements file')
    r = requests.get(url)

    if r.status_code != 200:
        raise NotebookManagementError('Failed to pull down requirements.txt file from S3')

    logger.info('Writing contents of requirements file')
    with open('requirements.txt', 'wb') as requirements:
        requirements.write(r.content)

    logger.info('Requirements file ready')


def post_save(git_enabled=False):

    def post_save_custom(model, os_path, contents_manager):
        """ Called from Jupyter post-save hook. Manages save of NB """

        if model['type'] != 'notebook':
            return
        logger.info('Getting URLs to update notebook')
        update_url, update_preview_url = get_update_urls()
        if not git_enabled:
            save_notebook(update_url, os_path)
        generate_and_save_preview(update_preview_url, os_path)
        logger.info('Notebook save complete')
    return post_save_custom


def get_update_urls():
    """
      Get the URLs needed to update the NB.
      These URLs expire after a few minutes so do not cache them
    """

    client = get_client()
    urls = client.notebooks.list_update_links(os.environ['PLATFORM_OBJECT_ID'])
    return (urls.update_url, urls.update_preview_url)


def save_notebook(url, os_path):
    """ Push raw notebook to S3 """
    with open(os_path, 'rb') as nb_file:
        logger.info('Pushing latest notebook file to S3')
        requests.put(url, data=nb_file.read())
        logger.info('Notebook file updated')


def generate_and_save_preview(url, os_path):
    """ Render NB-as-HTML and push that file to S3 """
    d, fname = os.path.split(os_path)
    logger.info('Rendering notebook to HTML')
    try:
        check_call(['jupyter', 'nbconvert', '--to', 'html', fname], cwd=d)
    except CalledProcessError as e:
        raise NotebookManagementError('nbconvert failed to convert notebook file to html: {}'.format(repr(e)))

    with open('notebook.html', 'rb') as preview_file:
        logger.info('Pushing latest notebook preview to S3')
        requests.put(url, data=preview_file.read())
        logger.info('Notebook preview updated')


def get_client():
    """ This gets a client that knows about our notebook endpoints """

    # TODO: Simplify this once the notebooks endpoints are in the client
    return civis.APIClient(resources='all')


def setup_logging():
    """ Set up log format """
    logger = logging.getLogger('CIVIS_PLATFORM_BACKEND')
    logger.setLevel(logging.INFO)
    # needed to remove duplicate log records..don't know why...
    logger.propagate = False
    # make sure to grab orig stderr since things seem to get redirected a bit
    # by the notebook and/or ipython...
    ch = logging.StreamHandler(stream=sys.__stderr__)
    formatter = logging.Formatter(
        fmt='[%(levelname).1s %(asctime)s %(name)s] %(message)s',
        datefmt="%H:%M:%S")
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


class NotebookManagementError(Exception):
    '''
    raised whenever we hit an error trying to move
    notebook data between our notebook and platform
    '''


logger = setup_logging()

from __future__ import unicode_literals, print_function

from collections import namedtuple
from datetime import datetime

import logging

from qordoba.languages import get_destination_languages
from qordoba.project import ProjectAPI

log = logging.getLogger('qordoba')


class FileStatus:
    error = 'Error'
    preparing = 'Preparing...'
    completed = 'Completed'
    enabled = 'Enabled'
    disabled = 'Disabled'


def get_status(page):
    status = ''
    if page.get('error_id'):
        status = FileStatus.error
    elif page.get('preparing'):
        status = FileStatus.preparing
    elif page.get('enabled') and page.get('completed'):
        status = FileStatus.completed
    elif page.get('enabled'):
        status = FileStatus.enabled
    elif not page.get('enabled'):
        status = FileStatus.disabled

    return status



class ResultRow(namedtuple('_ResultRow', ('id', 'name', 'segments', 'updated_on', 'status'))):
    pass


def ls_command(config):
    api = ProjectAPI(config)
    project = api.get_project()

    lang = next(get_destination_languages(project))

    for page in api.page_search(lang.id):
        if page.get('deleted', False):
            continue
        if page.get('version_tag', None):
            page_name = '{} [{}]'.format(page['url'], page['version_tag'])
        else:
            page_name = page['url']
        yield ResultRow(
            page['page_id'],
            page_name,
            page['segment_count'],
            datetime.fromtimestamp(page['update'] / 1e3),
            get_status(page)
        )

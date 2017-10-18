from __future__ import unicode_literals, print_function

import logging

from qordoba.commands.utils import ask_bool
from qordoba.languages import get_destination_languages
from qordoba.project import ProjectAPI

log = logging.getLogger('qordoba')


def delete_command(curdir, config, file_name, force=False):
    api = ProjectAPI(config)
    project = api.get_project()
    lang = next(get_destination_languages(project))

    page_id = None
    try:
        page_id = int(file_name)
    except ValueError:
        pass

    if not page_id:
        for page in api.page_search(lang.id, search_string=file_name):
            if page['url'] == file_name:
                page_id = page['page_id']
                break

    if page_id:
        if not force:
            if not ask_bool(
                    'Are you sure you want to delete `{}` and all translations for this resource?'.format(file_name)
            ):
                return

        api.delete_page(page_id)

    else:
        log.info('Resource `{}` not found.'.format(file_name))

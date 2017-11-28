from __future__ import unicode_literals, print_function

import logging

from qordoba.languages import init_language_storage
from qordoba.project import ProjectAPI
from qordoba.settings import load_settings, SettingsError, SettingsValidationError, \
    save_settings

log = logging.getLogger('qordoba')


def init_command(curpath, access_token, project_id, organization_id=None, force=False):
    try:
        config, loaded = load_settings(access_token=access_token, project_id=project_id,
                                       organization_id=organization_id)
    except SettingsValidationError:
        raise
    else:
        if loaded and force is False:
            raise SettingsError('Config file already exists.')

    api = ProjectAPI(config)

    log.info('Checking organization and project...')

    project = api.get_project()

    save_settings(config)

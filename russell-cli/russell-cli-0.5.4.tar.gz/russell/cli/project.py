import click
import traceback
import webbrowser
from tabulate import tabulate
from time import sleep
import sys

import russell
from russell.cli.utils import get_task_url, get_module_task_instance_id
from russell.client.common import get_url_contents
from russell.client.experiment import ExperimentClient
from russell.client.module import ModuleClient
from russell.client.task_instance import TaskInstanceClient
from russell.client.project import ProjectClient
from russell.config import generate_uuid
from russell.manager.auth_config import AuthConfigManager
from russell.manager.experiment_config import ExperimentConfigManager
from russell.manager.russell_ignore import RussellIgnoreManager
from russell.model.experiment_config import ExperimentConfig
from russell.log import logger as russell_logger
from russell.exceptions import *


# @click.option('--remote/--local', default=False, help='Init project from remote or not')
@click.command()
@click.option('--id',
              help='Remote project id to init')
@click.option('--name',
              help='Remote project name to init')
# @click.argument('project', nargs=1)
def init(id, name):
    """
    Initialize new project at the current dir.

        russell init --name test_name

    or

        russell init --id 151af60026cd462792fa5d77ef79be4d
    """
    if not id and not name:
        russell_logger.warning("Neither id or name offered\n{}".format(init.__doc__))
        return
    RussellIgnoreManager.init()
    access_token = AuthConfigManager.get_access_token()
    project_info = {}
    pc = ProjectClient()
    try:
        if id:
            project_info = pc.get_project_info_by_id(id=id)
        elif name:
            project_info = pc.get_project_info_by_name(access_token.username, name)
    except Exception as e:
        raise e
    else:
        project_id = project_info.get('id')
        name = project_info.get('name', '')
        latest_version = project_info.get('latest_version')
        if project_id:
            experiment_config = ExperimentConfig(name=name,
                                                 family_id=generate_uuid(),
                                                 project_id=project_id,
                                                 version=latest_version)
            ExperimentConfigManager.set_config(experiment_config)
            russell_logger.info("Project \"{}\" initialized in current directory".format(name))
        else:
            russell_logger.error("Project \"{}\" initialization failed in current directory".format(name))

@click.command()
@click.argument('project_url_or_id', nargs=1)
def clone(project_url_or_id):
    """
    Clone remote project at the current dir.
    """
    # experiment_config = ExperimentConfig(name=project,
                                         # family_id=generate_uuid())
    # ExperimentConfigManager.set_config(experiment_config)
    # RussellIgnoreManager.init()

    ProjectClient().clone(project_url_or_id,
                          uncompress=True,
                          delete_after_uncompress=True)


@click.command()
@click.argument('project_url_or_id', nargs=1)
def clone2(project_url_or_id):
    """
    For Development: Clone remote project at the current dir.
    """
    client = ProjectClient()
    try:
        project_name = str(client.get_project_name(project_url_or_id))
        russell_logger.debug(project_name)
        if not project_name or not isinstance(project_name, str) or not len(project_name) > 0:
            sys.exit("Project id is illegal or not found")
        else:
            url = client.url + 'clone/' + project_url_or_id
            for status in client.async_request_clone(url=url, api_version=2):
                if isinstance(status, dict):
                    if 'task_id' in status:
                        try:
                            client.download_compressed(url + "?task_id={}&stream=1".format(status.get('task_id')),
                                                   compression='zip',
                                                   uncompress=True,
                                                   delete_after_uncompress=True,
                                                   dir=project_name,
                                                   api_version=2)
                        except Exception as e:
                            russell_logger.error("Clone ERROR! {}".format(e))
                    else:
                        num = status.get('num')
                        size = status.get('size')
                        russell_logger.info("remote: " + str(num) + " files compressed")
                else:
                    russell_logger.error("Clone ERROR! {}".format("Please retry"))

    except Exception as e:
        russell_logger.error("Clone ERROR! {}".format(e))
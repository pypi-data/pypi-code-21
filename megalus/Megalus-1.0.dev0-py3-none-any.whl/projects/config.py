"""Config package for Megalus.

Define Setting class with processed data from project's
docker-compose.yaml saved on disk.
"""
import os
import yaml
from enum import auto
from buzio import console
from megalus.core.utils import AutoEnum


class AppType(AutoEnum):

    Backend = auto()
    Frontend = auto()
    Database = auto()
    Cache = auto()
    Broker = auto()


class Setting():
    """Setting Class."""

    def __init__(self, *args, **kwargs):
        """Function: __init__.

        self.project = Current Project Data Dict
        self.profile = Current User Data Dict
        self.data = data loaded from ~/.megalus/megconfig.yml
        self.compose = data from docker-compose.yml
        """
        self.project = None
        self.profile = None
        self.compose = None
        self.data = {
            'config': {
                'current': None
            },
            'projects': None
        }

    @property
    def has_project(self):
        """Property: has_project.

        Return
        ------
        Bool if project data exists
        """
        return self.project is not None

    @property
    def has_profile(self):
        """Property: has_profile.

        Return
        ------
        Bool if user data exists
        """
        return self.profile is not None

    @property
    def ready(self):
        """Function: ready.

        Return
        ------
        Bool if data is ready
        """
        return self.has_profile and self.has_project

    def get_data(self):
        """Function: get_data.

        Summary: Read project and user data from disk.
        """
        basepath = os.path.expanduser("~")
        self.path = os.path.join(basepath, ".megalus")
        projectfile = os.path.join(self.path, "megconfig.yml")

        # Create path
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        # Load data
        if os.path.isfile(projectfile):
            with open(projectfile, 'r') as file:
                self.data = yaml.loads(file.read())

        # Load current project
        if self.data['projects'] and self.data['config']['current']:
            self.project = \
                self.data['projects'][self.data['config']['current']]

        # Load user
        if self.project:
            profilefile = os.path.join(
                self.path, "{}.yml".format(
                    self.project['config_file']))
            if os.path.isfile(profilefile):
                with open(profilefile, 'r') as file:
                    self.profile = yaml.loads(file.read())

    def create_project(self):
        self.project = {
            "dc_version": "",
            "dc_path": "",
            "name": "",
            "config_file": "",
            "project_path": "",
            "env_vars": [],
            "use_vpn": False,
            "applications": [],
            "dockerfile_dev": "",
            "dockerfile_stage": "",
            "dockerfile_build": "",
            "vcs_name": "",
            "vcs_base_url": "",
            "vcs_api_url": "",
            "vcs_repository_url": "",
            "vcs_pull_request_url": "",
            "use_aws": False,
            "use_redis": False,
            "use_slack": False
        }
        os.system('cls' if os.name == 'nt' else 'clear')
        console.section("Criar novo Projeto", full_width=True)

        # Find Docker-compose.yml
        self.project['dc_path'] = console.ask(
            "Digite o caminho do arquivo Docker-Compose.yaml",
            validator=validate_yaml)
        with open(self.project['dc_path'], 'r') as file:
            self.compose = yaml.load(file.read())

        # Parse data from Docker-Compose.yml
        self.project['dc_version'] = self.compose['version']
        self.project['applications'] = [
            {
                'name': service['container_name']
                if 'container_name' in service else service,
                'base': 'build' if 'build' in service else 'image',
                'type': console.choose(
                        AppType.listall(),
                        question="Tipo de {}".format(service)
                ),
                'link': service.get('links', [])
            }
            for service in self.compose['services']
        ]

        # Fill another questions
        self.project['name'] = console.ask(
            "Digite o nome do Projeto", required=True)


def validate_yaml(path):
    try:
        with open(path, 'r') as file:
            yaml.load(file.read())
    except Exception as e:
        console.error(e)
        return False
    return True


settings = Setting()

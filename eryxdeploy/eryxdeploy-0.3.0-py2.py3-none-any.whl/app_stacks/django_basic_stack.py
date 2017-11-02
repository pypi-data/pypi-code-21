# coding=utf-8
import os

from fabric.context_managers import settings

from eryx_deploy.app_stacks.abs_app_stack import AppStack
from eryx_deploy.assets.databases.postgresql import PostgresDatabase
from eryx_deploy.assets.frameworks.django import DjangoProject
from eryx_deploy.assets.package_managers.frontend.null import NullPackageManager
from eryx_deploy.assets.package_managers.python.pip import Pip
from eryx_deploy.assets.vcs.git import Git
from eryx_deploy.assets.virtual_environments import Virtualenv
from eryx_deploy.assets.web_assets_pipelines.null import NullPipeline
from eryx_deploy.assets.webservers.python.ngnix_with_gunicorn import NgnixWithGunicornWebserver
from eryx_deploy.utils.interactive_console import InteractiveConsole


class DjangoBasicStack(AppStack):
    """
    Django stack
    """

    def __init__(self, host, project_name,
                 remote_url, virtual_env_path, requirements_file_path,
                 db_name, db_user, db_password,
                 db=PostgresDatabase, db_port='', db_client=None, db_server=None,
                 python_webserver=NgnixWithGunicornWebserver, wsgi_package=None,
                 vcs=Git,
                 python_package_manager=Pip,
                 virtual_env=Virtualenv,
                 web_assets_pipeline=NullPipeline,
                 frontend_package_manager=NullPackageManager,
                 has_custom_test_settings=False):
        """
        @param host: Machine where project will be deployed. Required.
        @param project_name: Project name that will be used for all configurations. Required.
        @param remote_url: You VCS repo url, like git@gitlab.com:eryx/myproject.git. Required.
        @param virtual_env_path: Full path to virtual env. Required.
        @param requirements_file_path: Relative path of requirements file used when deployed. Required.
        @param db_name: Database name. Required.
        @param db_user: Database user. Required.
        @param db_password: Database user's password. Required.
        @param db: Database class. Check assets/databases for options. Default: PostgresDatabase.
        @param db_port: Database port. Default: ''.
        @param db_client: Database client machine. Default: Host machine.
        @param db_server: Dabatase server machine. Default: Host machine.
        @param python_webserver: Webserver class. Check assets/webservers/python for options.
        Default: NgnixWithGunicornWebserver.
        @param wsgi_package: WSGI package for running the app with the webserver. Default: 'project_name.wsgi'
        @param vcs: VCS class. Default: Git.
        @param python_package_manager: PythonPackageManager subclass. Check assets/package_managers/python for options.
        @param virtual_env: VirtualEnvironment class. Check assets/environments/virtual_environments for options.
        Default: Virtualenv.
        @param web_assets_pipeline: WebAssetsPipeline subclass. Check assets/web_assets_pipeline for options.
        Default: NullPipeline (does nothing)
        @param frontend_package_manager: FrontendPackageManager subclass. Check assets/environments/virtual_environments
        for options. Default: NullPackageManager (does nothing).
        @param has_custom_test_settings: If the project uses a test_settings.py when running tests.
        """

        self._host_machine = host

        if db_client is None:
            db_client = self._host_machine

        if db_server is None:
            db_server = self._host_machine

        self._db = db(client_machine=db_client, server_machine=db_server, name=db_name, port=db_port, user=db_user,
                      password=db_password)

        self._vcs = vcs(client_machine=host, remote_url=remote_url)
        self._django_project = DjangoProject(host_machine=self._host_machine,
                                             project_name=project_name,
                                             db=self._db,
                                             virtual_env_path=virtual_env_path,
                                             requirements_file_path=requirements_file_path,
                                             virtual_env=virtual_env,
                                             python_package_manager=python_package_manager,
                                             web_assets_pipeline=web_assets_pipeline,
                                             frontend_package_manager=frontend_package_manager,
                                             has_custom_test_settings=has_custom_test_settings)
        if wsgi_package is None:
            wsgi_package = '%s.wsgi' % project_name
        self._python_webserver = python_webserver(machine=host, webapp_name=project_name,
                                                  wsgi_package=wsgi_package,
                                                  virtual_env_path=virtual_env_path)

    # tasks

    def host_machine(self):
        return self._host_machine

    def db(self):
        return self._db

    def install(self):
        self._host_machine.install_python_lib()
        self._db.install_server()
        self._db.install_client()

        self._host_machine.create_project_folder()

        django_project_dir = os.path.join(self._host_machine.project_path(),
                                          self._django_project.project_name())

        if not self._host_machine.path_exists(django_project_dir):
            self._vcs.clone_project()

        self._django_project.first_time_setup()

        self._python_webserver.configure_server()
        self._python_webserver.restart_server()

    def upgrade(self):
        self._vcs.pull()

        self._django_project.after_pull_update()

        self._python_webserver.restart_server()

    def rollback_db_to_latest_backup(self):
        self._host_machine.latest_db_dump_datetime(self._db.name())

        question = "El último backup tiene fecha el %s, ¿continuar?"
        answer = InteractiveConsole.yes_or_no(question, default=True)

        if answer:
            db_dump_filename = self._host_machine.latest_db_dump_filename(database_name=self._db.name())
            self._reload_db_from_dump(db_dump_filename)
        else:
            InteractiveConsole.abort()

    # private

    # TODO
    #  Move this to Database class. It should warn MUCH MORE if DB is remote instead of local!
    #  Check also SyncLocalDBTask.
    def _reload_db_from_dump(self, dump_filename):
        if self._host_machine.path_exists(dump_filename):
            if InteractiveConsole.yes_or_no("La base de datos REMOTA será BORRADA. ¿Desea continuar?", default=False):
                with settings(warn_only=True):
                    result = self._db.drop_db()
                    InteractiveConsole.show_info(result.return_code)

                self._host_machine.create()
                self._host_machine.load_dump(dump_input_path=dump_filename)
            else:
                InteractiveConsole.abort()
        else:
            InteractiveConsole.abort("No se encontro el archivo %s!" % dump_filename)

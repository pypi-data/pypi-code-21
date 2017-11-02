import os

from eryx_deploy.assets.frameworks.abs_framework import FrameworkProject
from eryx_deploy.assets.package_managers.frontend.null import NullPackageManager
from eryx_deploy.assets.package_managers.python.pip import Pip
from eryx_deploy.assets.virtual_environments import Virtualenv
from eryx_deploy.assets.web_assets_pipelines.null import NullPipeline
from eryx_deploy.utils.interactive_console import InteractiveConsole


class DjangoProject(FrameworkProject):
    def __init__(self, host_machine, project_name, db, virtual_env_path, requirements_file_path,
                 virtual_env=Virtualenv,
                 python_package_manager=Pip,
                 web_assets_pipeline=NullPipeline,
                 frontend_package_manager=NullPackageManager,
                 has_custom_test_settings=False):
        super(DjangoProject, self).__init__(machine=host_machine, project_name=project_name)

        self._db = db

        self._virtual_environment = virtual_env(host_machine=host_machine, name=project_name, path=virtual_env_path)

        self._python_package_manager = python_package_manager(virtual_environment=self._virtual_environment,
                                                              requirements_file_path=requirements_file_path)

        self._assets_pipeline = web_assets_pipeline(host_machine=self._host_machine)

        self._frontend_package_manager = frontend_package_manager(host_machine=self._host_machine)

        self._has_custom_test_settings = has_custom_test_settings

    def first_time_setup(self):
        self._python_package_manager.first_time_setup()
        self._configure_local_settings()
        self._db.create()
        self._frontend_package_manager.first_time_setup()
        self._assets_pipeline.first_time_setup()

        self.after_pull_update()

    def after_pull_update(self):
        self._python_package_manager.update_dependencies()
        self.migrate()
        self._frontend_package_manager.update_dependencies()
        self._assets_pipeline.run_pipeline()
        self.collect_static()

    # helpers

    def migrate(self):
        with self._cd_project():
            self._host_machine.create_db_dump_of(self._db)

        self._virtual_environment.run('python manage.py migrate')

    def collect_static(self):
        self._virtual_environment.run('python manage.py collectstatic --noinput')

    def run_tests(self):
        if self._has_custom_test_settings:
            self._host_machine.run('python manage.py test --settings="%s.test_settings"' % self._project_name)
        else:
            self._host_machine.run('python manage.py test')

    # private

    def _configure_local_settings(self):
        with self._cd_project():
            if self._host_machine.path_exists(os.path.join(self.project_name(), 'local_settings.py')):
                return

            if self._host_machine.path_exists('%s/local_settings.example.py' % self._project_name):
                self._host_machine.run('cp %(local_settings_path)s/local_settings.example.py '
                                       '%(local_settings_path)s/local_settings.py' % {
                                           'local_settings_path': self._project_name
                                       })
            else:
                InteractiveConsole.abort_with_suggestion("Cannot find file 'local_settings.example.py' for project. "
                                                         "Please check that the file exists in project's repo.")

            allowed_host_settings = "\nALLOWED_HOSTS = ['%s']\n" % self._host_machine.hostname()
            self._host_machine.append('%s/local_settings.py' % self._project_name, allowed_host_settings)

            self._host_machine.append('%s/local_settings.py' % self._project_name, self._database_settings())

    def _database_settings(self):
        if self._db.engine() == 'postgresql':
            db_engine = 'postgresql_psycopg2'  # for Django <= 1.8 support (compatible with newer versions also)
        else:
            db_engine = self._db.engine()

        settings = '\n'
        settings += "DATABASES = {\n" + \
                    "\t\'default\': {\n" + \
                    "\t\t\'ENGINE\': \'django.db.backends.%(database_engine)s\',\n" + \
                    "\t\t\'NAME\': \'%(database_name)s\',\n" + \
                    "\t\t\'USER\': \'%(database_user)s\',\n" + \
                    "\t\t\'PASSWORD\': \'%(database_password)s\',\n" + \
                    "\t\t\'HOST\': \'%(database_host)s\',\n" + \
                    "\t\t\'PORT\': \'%(database_port)s\',\n" + \
                    "\t}\n" + \
                    "}\n"

        return settings % {
            'database_name': self._db.name(),
            'database_password': self._db.password(),
            'database_host': self._db.host(),
            'database_engine': db_engine,
            'database_user': self._db.user(),
            'database_port': self._db.port(),
        }

    def _cd_project(self):
        return self._host_machine.cd_project()

import os
import importlib
import subprocess

from setuptools import Command


class build_static(Command):
    description = 'Runs `yarn install` and `yarn run compile` for the static files.'
    user_options = [
        ('static-dir-path=', None, 'The directory containing yarn, relative to the project root.',)
    ]

    def initialize_options(self):
        package_name = self.distribution.packages[0] # type: str
        package_module = importlib.import_module(package_name) # type: object
        package_path = os.path.dirname(package_module.__file__) # type: str
        # noinspection PyAttributeOutsideInit
        self.static_dir_path = '{package_path}/static/{app_name}/'.format(
            package_path=package_path,
            app_name=package_name,
        )
    
    def run(self):
        os.chdir(self.static_dir_path)
        subprocess.run(['yarn', 'install', '--pure-lockfile'], check=True)
        subprocess.run(['yarn', 'run', 'compile'], check=True)

    def finalize_options(self):
        pass

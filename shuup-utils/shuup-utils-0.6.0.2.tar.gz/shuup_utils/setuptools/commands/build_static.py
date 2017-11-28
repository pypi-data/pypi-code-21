import os
import importlib
import subprocess

from setuptools import Command


# noinspection PyAttributeOutsideInit
class BuildStaticCommand(Command):
    description = 'Runs `yarn install` and `yarn run compile` for the static files.'
    user_options = [(
        'yarn-dir-path=',
        None,
        'The directory containing yarn, relative to the project root.',
    )]

    def initialize_options(self):
        self.yarn_dir_path = get_default_yarn_dir_path(command=self)
    
    def run(self):
        build_static(self.yarn_dir_path)

    def finalize_options(self):
        pass


# TODO move out some `utils` and rename `BuildStaticCommand` into `build_static`
def build_static(yarn_dir_path: str = None):
    os.chdir(yarn_dir_path)
    subprocess.run(['yarn', 'install', '--pure-lockfile'], check=True)
    subprocess.run(['yarn', 'run', 'compile'], check=True)


def get_default_yarn_dir_path(command: Command) -> str:
    package_name = command.distribution.packages[0] # type: str
    package_module = importlib.import_module(package_name) # type: object
    package_path = os.path.dirname(package_module.__file__) # type: str
    return '{package_path}/static/{app_name}/'.format(
        package_path=package_path,
        app_name=package_name,
    )

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


def build_static(yarn_dir_path: str):
    _install_static_depenencies(yarn_dir_path)
    _compile_static_files(yarn_dir_path)


def get_default_yarn_dir_path(command: Command) -> str:
    package_name = command.distribution.packages[0] # type: str
    package_module = importlib.import_module(package_name) # type: object
    package_path = os.path.dirname(package_module.__file__) # type: str
    return '{package_path}/static/{app_name}/'.format(
        package_path=package_path,
        app_name=package_name,
    )


def _install_static_depenencies(yarn_dir_path: str):
    subprocess.run(
        ['yarn', 'install', '--pure-lockfile', '--cwd={}'.format(yarn_dir_path)],
        check=True,
    )


def _compile_static_files(yarn_dir_path: str):
    subprocess.run(
        ['yarn', 'run', '--cwd={}'.format(yarn_dir_path), 'compile'],
        check=True,
    )

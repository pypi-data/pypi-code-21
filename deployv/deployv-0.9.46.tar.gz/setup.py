# coding: utf-8

import os
import sys
import errno
import logging
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser
from setuptools.command.install import install as InstallCommand
from setuptools.command.test import test as TestCommand

logging.basicConfig()
_logger = logging.getLogger(__name__)  # pylint: disable=C0103

if os.environ.get('USER', '') == 'vagrant':
    del os.link

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


def _fix_ownership(path):
    uid = os.environ.get('SUDO_UID')
    gid = os.environ.get('SUDO_GID')
    if uid is not None:
        os.chown(path, int(uid), int(gid))


class PyInstall(InstallCommand):

    def run(self):
        InstallCommand.run(self)
        self.setup_config_dirs()

    def setup_config_dirs(self):
        sys.stdout.write("Writing config files\n")
        default_config_file = 'deployv/config/deployv.conf'
        for main_dir in ['/etc/deployv', os.path.expanduser('~/.config/deployv')]:
            config_file_name = os.path.join(main_dir, 'deployv.conf')
            error_msg = "Couldn't write config file: '{file}' (skipped)\n"
            ok_msg = "Created config file: '{file}'\n"
            addon_dir = os.path.join(main_dir, 'conf.d')
            is_user_dir = os.path.expanduser('~/') in main_dir
            try:
                os.makedirs(addon_dir)
            except OSError as error:
                if error.errno != errno.EEXIST:
                    sys.stdout.write(error_msg.format(file=config_file_name))
                    continue
            else:
                if is_user_dir:
                    for path in [main_dir.replace('/deployv', ''), main_dir, addon_dir]:
                        _fix_ownership(path)
            config = ConfigParser()
            config.read([default_config_file, config_file_name])
            try:
                with open(config_file_name, 'w+') as config_file:
                    config.write(config_file)
            except (OSError, IOError) as error:
                sys.stdout.write(error_msg.format(file=config_file_name))
            else:
                sys.stdout.write(ok_msg.format(file=config_file_name))
                if is_user_dir:
                    _fix_ownership(config_file_name)


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


readme = open('README.md').read()
requirements = open('requirements.txt').readlines()
test_requirements = open('test-requirements.txt').readlines()

setup(
    name='deployv',
    version='0.9.46',
    description='Base for all clases and scripts in VauxooTools',
    long_description=readme,
    package_data={'': [
        'templates/files/*', 'templates/*.jinja', 'config/*', 'helpers/json_schemas/*',
    ]},
    author='Tulio Ruiz',
    author_email='tulio@vauxoo.com',
    url='https://github.com/vauxoo/deployv',
    download_url='https://github.com/vauxoo/deployv',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='vauxootools deployv',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    tests_require=test_requirements,
    cmdclass={
        'install': PyInstall,
        'test': PyTest
    },
    py_modules=['deployv'],
    entry_points='''
        [console_scripts]
        deployvcmd=deployv.commands.deployvcmd:cli
        workerv=deployv.commands.workerv:run
    ''',
    scripts=[]
)

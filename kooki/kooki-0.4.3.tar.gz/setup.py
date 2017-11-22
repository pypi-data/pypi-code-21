#!/usr/bin/env python
import os, sys
from setuptools import setup, find_packages

__version__ = '0.4.3'

APP_NAME = 'kooki'
DESCRIPTION = 'The ultimate document generator.'
CONFIG_PATH = '/usr/share/kooki'


if 'install' in sys.argv:
    from pkg_resources import Requirement, resource_filename
    import os
    import shutil

    conf_path_temp = resource_filename(Requirement.parse(APP_NAME), 'jars')

    if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_PATH)

    for file_name in os.listdir(conf_path_temp):
        file_path_full = os.path.join(conf_path_temp, file_name)
        if os.path.isfile(file_path_full):
            shutil.copy(file_path_full, CONFIG_PATH)


datadir = os.path.join('jars')
data_files = [(os.path.join('/usr/share/kooki', d), [os.path.join(d,f) for f in files])
    for d, folders, files in os.walk(datadir)]


setup(
    name=APP_NAME,
    version=__version__,
    description=DESCRIPTION,
    author='Noel Martignoni',
    author_email='noel@martignoni.fr',
    url='https://gitlab.com/kooki/kooki',
    scripts=['scripts/kooki'],
    install_requires=['markdown', 'empy', 'pyyaml', 'toml', 'requests', 'termcolor', 'vcstool', 'libsass'],
    packages=find_packages(exclude=['tests*', 'jars']),
    test_suite='tests',
    data_files=data_files,
)

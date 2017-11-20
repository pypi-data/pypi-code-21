#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
from setuptools import setup


version = '2017.11.20'
frozen_name = 'medved/frozen.py'
url = 'https://soft.snbl.eu/_sources/medved.rst.txt'
token = '.. MEDVED Versions'
text = 'A new version of Medved is available at <a href=https://soft.snbl.eu/medved.html#download>soft.snbl.eu</a>'
we_run_setup = False
if not os.path.exists(frozen_name):
    we_run_setup = True
    hash_ = subprocess.Popen(['hg', 'id', '-i'], stdout=subprocess.PIPE).stdout.read().decode().strip()
    print(f'Medved mercurial hash is {hash_}')
    print('Creating frozen.py...\n', '*' * 40)
    with open(frozen_name, 'w') as frozen:
        s = (f'# -*- coding: utf-8 -*-\n\nhg_hash = "{hash_}"\nversion = "{version}"\nurl = "{url}"\ntoken = "{token}"'
             f'\ntext = "{text}"\n')
        frozen.write(s)
        print(s, '*' * 40)
        print('Done')

setup(
    name='medved',
    version=version,
    description='Modulation Enhanced Diffraction Viewer and EDitor',
    author='Vadim Dyadkin',
    author_email='diadkin@esrf.fr',
    url='https://soft.snbl.eu/medved.html',
    license='GPLv3',
    long_description='Do not forget to cite: https://doi.org/10.1107/S2053273316008378',
    install_requires=[
        'numpy',
        'scipy',
        'fortranformat',
        'qtsnbl',
    ],
    entry_points={
        'console_scripts': [
            'medved=medved.__init__:main',
        ],
    },
    packages=[
        'medved',
        'medved.ui',
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
if we_run_setup:
    print('Remove frozen.py')
    os.remove(frozen_name)

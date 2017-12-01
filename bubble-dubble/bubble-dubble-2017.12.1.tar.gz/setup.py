#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
from setuptools import setup


package_name = 'bubble'
package_version = '2017.12.1'


frozen_name = 'bubble/frozen.py'
we_run_setup = False
if not os.path.exists(frozen_name):
    we_run_setup = True
    hash_ = subprocess.Popen(['hg', 'id', '-i'], stdout=subprocess.PIPE).stdout.read().decode().strip()
    print(f'Bubble mercurial hash is {hash_}')
    with open(frozen_name, 'w') as frozen:
        frozen.write(f'# -*- coding: utf-8 -*-\nhg_hash = "{hash_}"\nversion = "{package_version}"\n')


setup(
    name='bubble-dubble',
    version=package_version,
    description='Azimuthal powder integration',
    author='Vadim Dyadkin',
    author_email='dyadkin@gmail.com',
    url='https://hg.3lp.cx/bubble',
    license='GPLv3',
    install_requires=[
        'numpy>=1.9',
        'cryio>=2016.11.20',
        'integracio>=2016.12.14',
        'decor>=2017.5.12',
        'pyqtgraph>=0.10.0',
        'Pillow',
        'scipy',
    ],
    entry_points={
        'console_scripts': [
            f'bubbles={package_name}.bserver.__init__:main',
        ],
        'gui_scripts': [
            f'bubblec={package_name}.bclient.__init__:main',
        ],
    },
    packages=[
        'bubble',
        'bubble.bclient',
        'bubble.bclient.ui',
        'bubble.bcommon',
        'bubble.bserver',
    ],
)


if we_run_setup:
    os.remove(frozen_name)

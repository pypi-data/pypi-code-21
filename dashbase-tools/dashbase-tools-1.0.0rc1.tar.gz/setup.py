import platform
import sys

from setuptools import setup, find_packages

if sys.version_info < (2, 7):
    sys.exit('Sorry, Python < 2.7 is not supported')
if sys.version_info.major > 2:
    sys.exit('Sorry, Python >= 3 is not supported')
if platform.system() == 'Windows':
    sys.exit('Sorry, Windows is not supported')

setup(
    name='dashbase-tools',
    version='1.0.0rc1',
    url='http://www.dashbase.io',
    maintainer='khou',
    maintainer_email='kevin@dashbase.io',
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    install_requires=[
        'colorama==0.3.7',
        'dateparser==0.6.0',
        'fusepy==2.0.4',
        'ruamel.ordereddict==0.4.13',
        'setuptools>=12.2',
        'simplejson==3.12.0',
        'termcolor==1.1.0',
        'terminaltables==3.1.0',
        'treelib==1.4.0',
        'urllib3==1.22',
    ],
    scripts=['scripts/dashbase_umnt'],
    entry_points='''
        [console_scripts]
        dash=tools.dbsql:main
        logtail=tools.logtail:main
        dashbase_mnt=tools.dashbase_mnt:main
    ''',
)

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
    version='0.0.1',
    url='http://www.dashbase.io',
    maintainer='khou',
    maintainer_email='kevin@dashbase.io',
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    install_requires=[
        'setuptools>=12.2',
        'urllib3==1.21.1',
        'dateparser==0.6.0',
        'terminaltables==3.1.0',
        'simplejson==3.11.1'
    ],
    entry_points='''
        [console_scripts]
        dash=tools.dbsql:main
        logtail=tools.logtail:main
    '''
)

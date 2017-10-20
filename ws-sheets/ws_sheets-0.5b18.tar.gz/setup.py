import os
import re
import json
from setuptools import setup

with open('Setup.lock') as f:
    c = json.loads(f.read())

with open(os.path.join(c['name'], '__init__.py')) as f:
    version = re.findall("^__version__ = '(.*)'", f.read())[0]

with open('Pipfile.lock') as f:
    p = json.loads(f.read())

def _install_requires():
    with open('requirements.txt') as f:
        s = f.read()
    s = s.strip().split('\n')
    s = [s.strip() for s in s]
    print(s)
    return s

install_requires = list(_install_requires())

kwargs = {
        'name': c['name'],
        'version': version,
        'description': c['description'],
        'url': c['url'],
        'author': c['author'],
        'author_email': c['author_email'],
        'license': c['license'],
        'packages': c.get('packages', []),
        'zip_safe': False,
        'scripts': c.get('scripts',[]),
        'package_data': c.get('package_data',{}),
        'install_requires': install_requires,
        'classifiers': c.get('classifiers', [])
        }

setup(**kwargs)




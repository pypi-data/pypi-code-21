# -*- coding: utf-8 -*-

import sys

import os
from setuptools import setup
from setuptools import find_packages

reload(sys)
sys.setdefaultencoding('utf-8')

local_path = lambda *f: os.path.join(os.path.dirname(__file__), *f)
local_file = lambda *f: open(local_path(*f), 'rb').read()

dependencies = filter(bool, map(bytes.strip, local_file('requirements.txt').splitlines()))

# https://setuptools.readthedocs.io/en/latest/setuptools.html#adding-setup-arguments
setup(
    name='p4rr0t007',
    version='0.3.7',
    description="\n".join([
        'h1gh lEv3l fl4sk 4 h4x0rs'
    ]),
    author=u"Ð4√¡η¢Ч",
    author_email='d4v1ncy@protonmail.ch',
    url=u'https://github.com/c0ntrol-x/p4rr0t007',
    packages=find_packages(exclude=['*tests*']),
    install_requires=dependencies,
    include_package_data=True,
    package_data={
        'p4rr0t007': 'include COPYING *.txt *.rst docs/* docs/build/* docs/build/doctrees/* docs/build/html/* docs/build/html/_sources/* docs/build/html/_static/* docs/build/html/_static/css/* docs/build/html/_static/fonts/* docs/build/html/_static/js/* docs/source/* docs/source/_static/* docs/source/_templates/* docs/source/_webroot/*'.split(),
    },
    zip_safe=False,
)

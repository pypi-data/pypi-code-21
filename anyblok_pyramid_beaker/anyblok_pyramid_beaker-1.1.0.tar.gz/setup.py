# This file is a part of the AnyBlok / Pyramid / Beaker project
#
#    Copyright (C) 2016 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from setuptools import setup, find_packages
import os
version = '1.1.0'

requires = [
    'anyblok_pyramid>=0.7.0',
    'pyramid_beaker',
]

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), 'r', encoding='utf-8') as readme:
    README = readme.read()

with open(
    os.path.join(here, 'doc', 'FRONT.rst'), 'r', encoding='utf-8'
) as front:
    FRONT = front.read()

with open(
    os.path.join(here, 'doc', 'CHANGES.rst'), 'r', encoding='utf-8'
) as change:
    CHANGE = change.read()


anyblok_pyramid_settings = [
    'beaker_settings=anyblok_pyramid_beaker.pyramid_config:beaker_settings',
],

anyblok_pyramid_includeme = [
    'pyramid_beaker=anyblok_pyramid_beaker.pyramid_config:pyramid_beaker',
]

anyblok_pyramid_init = [
    'anyblok_pyramid_config=anyblok_pyramid_beaker:anyblok_init_config',
]

setup(
    name="anyblok_pyramid_beaker",
    version=version,
    author="Jean-Sébastien Suzanne",
    author_email="jssuzanne@anybox.fr",
    description="Beaker session for AnyBlok / Pyramid",
    license="MPL2",
    long_description=README + '\n' + FRONT + '\n' + CHANGE,
    url="http://docs.anyblok-pyramid-beaker.anyblok.org/" + version,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=requires,
    tests_require=requires + ['nose', 'WebTest'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Pyramid',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
    ],
    entry_points={
        'anyblok.init': anyblok_pyramid_init,
        'anyblok_pyramid.settings': anyblok_pyramid_settings,
        'anyblok_pyramid.includeme': anyblok_pyramid_includeme,
    },
    extras_require={},
)

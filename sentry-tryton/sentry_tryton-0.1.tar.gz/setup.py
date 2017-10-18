# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='sentry_tryton',
    version='0.1',
    author='Sergi Almacellas Abellana',
    author_email='sergi@koolpi.com',
    url='https://bitbucket.org/pokoli/sentry-tryton/',
    description='Sentry Integration for the Tryton Framework',
    long_description=read('README'),
    py_modules=['sentry_tryton'],
    zip_safe=False,
    platforms='any',
    keywords='sentry tryton',
    classifiers=[
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    license='GPL-3',
    install_requires=[
        'raven',
        'trytond>=4.2',
        ],
    )

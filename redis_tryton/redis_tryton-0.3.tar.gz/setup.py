# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='redis_tryton',
    version='0.3',
    author='Sergi Almacellas Abellana',
    author_email='sergi@koolpi.com',
    url='https://bitbucket.org/pokoli/redis-tryton/',
    description='Redis Cache for the Tryton Framework',
    long_description=read('README'),
    py_modules=['redis_tryton'],
    zip_safe=False,
    platforms='any',
    keywords='redis tryton cache',
    classifiers=[
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    license='GPL-3',
    install_requires=[
        'redis',
        'msgpack-python',
        'trytond>=4.2',
        ],
    )

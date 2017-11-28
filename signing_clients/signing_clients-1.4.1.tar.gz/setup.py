import sys
import os
import codecs
from setuptools import setup, find_packages

version = '1.4.1'

# Helper to publish to pypi. Just call `python setup.py publish`
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    print('You probably want to also tag the version now:')
    print('  git tag -a %s -m "version %s"' % (version, version))
    print('  git push --tags')
    sys.exit()


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


setup(
    name='signing_clients',
    version=version,
    description='Applications signature/manifest manipulator and receipt verifier',
    long_description=read('README.md'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    keywords='web services',
    author='Ryan Tilder',
    author_email='service-dev@mozilla.com',
    url='https://github.com/mozilla/signing-clients/',
    install_requires=[
        'asn1crypto>=0.23',
        'six>=1.10.0'
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='signing_clients.tests'
)

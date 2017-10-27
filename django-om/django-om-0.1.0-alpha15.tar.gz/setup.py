import os
import re

from distutils.core import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('django_om')

setup(
    name='django-om',
    packages=['django_om'],
    version=version,
    description='Om.next query parser for Django',
    author='Chargeads',
    author_email='devs@chargeads.com',
    url='https://github.com/chargeads/django-om',
    download_url='https://github.com/chargeads/django-om/tarball/0.1',
    keywords=['django', 'om', 'next', 'query', 'parser'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.7',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

import os
import re

from setuptools import setup, find_packages


def get_long_description():
    for filename in ('README.rst',):
        with open(filename, 'r') as f:
            yield f.read()


def get_version(package):
    with open(os.path.join(package, '__init__.py')) as f:
        pattern = r'^__version__ = [\'"]([^\'"]*)[\'"]'
        return re.search(pattern, f.read(), re.MULTILINE).group(1)


setup(
    name='django-core-flavor',
    version=get_version('core_flavor'),
    license='MIT',
    description='A Django application that provides core tools.',
    long_description='\n\n'.join(get_long_description()),
    author='mongkok',
    author_email='dani.pyc@gmail.com',
    maintainer='mongkok',
    url='https://github.com/flavors/core/',
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'Django>=1.10',
        'django-model-utils>=3.0.0',
        'django-oauth-toolkit>=0.12.0',
        'djangorestframework>=3.5.0',
        'elastic-sdk>=0.0.1',
        'psycopg2>=2.6.2'
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
    ],
    zip_safe=False,
    tests_require=[
        'Django>=1.10',
        'django-model-utils>=3.0.0',
        'django-oauth-toolkit>=0.12.0',
        'djangorestframework>=3.5.0',
        'elastic-sdk>=0.0.1',
        'factory-boy>=2.8.1',
        'Faker>=0.7.11',
        'psycopg2>=2.6.2'
    ],
    package_data={
        'core_flavor': [
            'locale/*/LC_MESSAGES/django.po',
            'locale/*/LC_MESSAGES/django.mo'
        ]
    }
)

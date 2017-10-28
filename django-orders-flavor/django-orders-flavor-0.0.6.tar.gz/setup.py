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
    name='django-orders-flavor',
    version=get_version('orders'),
    license='MIT',
    description='Django app for orders',
    long_description='\n\n'.join(get_long_description()),
    author='mongkok',
    author_email='dani.pyc@gmail.com',
    maintainer='mongkok',
    url='https://github.com/flavors/orders/',
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'Django>=1.11',
        'django-core-flavor>=0.0.20',
        'django-countries-flavor>=0.0.7',
        'django-filter>=1.0.2',
        'django-model-utils>=3.0.0',
        'django-oauth-toolkit>=0.12.0',
        'django-paypal>=0.3.6',
        'django-polymorphic>=1.2',
        'djangorestframework>=3.6.3',
        'Pillow>=4.1.1',
        'sorl-thumbnail>=12.3'
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
        'Django>=1.11',
        'coverage>=4.4',
        'django-core-flavor>=0.0.20',
        'django-countries-flavor>=0.0.7',
        'django-filter>=1.0.2',
        'django-model-utils>=3.0.0',
        'django-oauth-toolkit>=0.12.0',
        'django-paypal>=0.3.6',
        'django-polymorphic>=1.2',
        'djangorestframework>=3.6.3',
        'factory-boy>=2.8.1',
        'Faker>=0.7.11',
        'Pillow>=4.1.1',
        'sorl-thumbnail>=12.3'
    ],
    package_data={
        'orders': [
            'templates/orders/*',
            'locale/*/LC_MESSAGES/django.po',
            'locale/*/LC_MESSAGES/django.mo'
        ]
    }
)

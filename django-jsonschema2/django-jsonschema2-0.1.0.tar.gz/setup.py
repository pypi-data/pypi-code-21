import os
from setuptools import setup, find_packages

VERSION = '0.1.0'
PATH = os.path.dirname(os.path.abspath(__file__))


def read(fname):
    return open(os.path.join(PATH, fname)).read()


install_requires = [
    'jsonschema',
    'django',
]

setup(
    name='django-jsonschema2',
    version=VERSION,
    description='Django JSONSchema',
    long_description=read('README.md'),
    url='https://github.com/hypc/django-jsonschema',
    author='hypc',
    author_email='h_yp00@163.com',
    license='MIT',
    packages=find_packages(exclude=['docs', 'tests*', 'example']),
    requires=install_requires,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers',
        'Topic :: Internet',
    ]
)

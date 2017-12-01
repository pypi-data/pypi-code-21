import io
import os

from setuptools import find_packages, setup

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
README = io.open(os.path.join(BASE_DIR, 'README.md'), encoding='utf8').read()

version = '0.1'
author = 'Javier Matos Odut'
description = """
Yenviron allows to use 12factor inspired environment variables to configure
your Django application. It uses YAML files to store variables so it can be
easily integrated with ansible.
""".strip().replace('\n', ' ')

setup(
    name='yenviron',
    packages=find_packages(),
    version=version,
    description=description,
    long_description=README,
    author=author,
    author_email='iam@javiermatos.com',
    url='https://github.com/javiermatos/yenviron',
    download_url='https://github.com/javiermatos/yenviron/archive/0.1.tar.gz',
    install_requires=[
        'PyYAML',
    ],
    license='MIT License',
    keywords='django ansible environment variables settings configuration',
    classifiers=[
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Framework :: Django',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
)

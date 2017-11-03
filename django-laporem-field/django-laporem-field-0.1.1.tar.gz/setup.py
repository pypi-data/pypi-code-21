import codecs
import os
import re
import sys

from setuptools import find_packages, setup


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="django-laporem-field",
    version=find_version("laporem_field", "__init__.py"),
    description="Easy gallery in one field at Django",
    long_description=open('README.rst').read(),
    author="magisterlaporem",
    author_email="magisterlaporem@gmail.com",
    url="https://bitbucket.org/magisterlaporem/django-laporem-field",
    packages=find_packages(),
    install_requires=[
        'django>=1.9.13',
        'pillow<4' if sys.version_info < (2, 7) else 'pillow',
        'easy-thumbnails>=2.4.2',
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: BSD License',
    ],
)

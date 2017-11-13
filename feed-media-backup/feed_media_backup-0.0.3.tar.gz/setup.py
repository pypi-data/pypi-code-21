"""feed_media_backup."""

# pylint: disable=missing-docstring

import ast
import os
import re
import sys
from shutil import rmtree

from setuptools import Command, setup

NAME = 'feed_media_backup'
DESCRIPTION = 'Backups media from blog RSS feeds.'
URL = 'https://github.com/xsteadfastx/feed_media_backup'
EMAIL = 'marvin@xsteadfastx.org'
AUTHOR = 'Marvin Steadfast'


REQUIRES = [
    'beautifulsoup4>=4.6.0',
    'click>=6.7',
    'feedparser>=5.2.1',
    'logzero>=1.3.0',
    'lxml>=3.8.0',
    'tinydb>=3.4.0',
    'typing>=3.6.2',
    'youtube-dl>=2017.8.18',
]

# get version
_version_re = re.compile(r'__version__\s+=\s+(.*)')
with open('src/feed_media_backup/__init__.py', 'r') as f:
    VERSION = str(ast.literal_eval(_version_re.search(f.read()).group(1)))


def _convert_readme():
    try:
        import pypandoc
        return pypandoc.convert('README.md', 'rst')
    except (IOError, ImportError):
        return ''


LONG_DESCRIPTION = _convert_readme()
if not LONG_DESCRIPTION:
    with open('README.md', 'r') as f:
        LONG_DESCRIPTION = f.read()


class PublishCommand(Command):
    """Support setup.py publish."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.sep.join(('.', 'dist')))
        except FileNotFoundError:
            pass

        long_description = _convert_readme()
        if long_description:

            self.status('Building Source and Wheel (universal) distribution…')
            os.system(
                '{0} setup.py sdist bdist_wheel --universal'.format(
                    sys.executable
                )
            )

            self.status('Uploading the package to PyPi via Twine…')
            os.system('twine upload dist/*')

            sys.exit()

        else:
            self.status('Problem with Pandoc!')
            sys.exit(1)


setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license='MIT',
    package_dir={'': 'src'},
    packages=['feed_media_backup'],
    install_requires=REQUIRES,
    entry_points='''
        [console_scripts]
        feed_media_backup=feed_media_backup.cli:main
    ''',
    cmdclass={
        'publish': PublishCommand,
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

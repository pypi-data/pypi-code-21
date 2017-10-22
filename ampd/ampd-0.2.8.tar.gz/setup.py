# coding: utf-8

from setuptools import setup, find_packages
import codecs
import os

from ampd import __version__ as version
# from ampd import __doc__ as long_description

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ampd',
    version=version,
    author='Itaï BEN YAACOV',
    author_email='candeb@free.fr',
    url='http://math.univ-lyon1.fr/~begnac',
    download_url='http://math.univ-lyon1.fr/~begnac/debian/gampc',
    description='Asynchronous MPD client library',
    long_description=long_description,
    license='GPLv3+',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['mpd', 'Music Player Deamon', 'asynchronous'],
    packages=find_packages(),
    install_requires=['decorator'],
)

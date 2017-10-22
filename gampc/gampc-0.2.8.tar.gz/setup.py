# coding: utf-8

from setuptools import setup, find_packages
from babel.messages import frontend as babel
# import codecs
# import os

from gampc import __version__ as version
from gampc import __doc__ as long_description

# with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'DESCRIPTION.rst'), encoding='utf-8') as f:
#    long_description = f.read()

setup(
    name='gampc',
    version=version,
    author='Itaï BEN YAACOV',
    author_email='candeb@free.fr',
    url='http://math.univ-lyon1.fr/~begnac',
    download_url='http://math.univ-lyon1.fr/~begnac/debian/gampc',
    description='Graphical Asynchronous Music Player Client',
    long_description=long_description,
    license='GPLv3+',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
    keywords=['mpd', 'Music Player Deamon', 'client'],
    packages=find_packages() + ['gampc.plugins'],
    package_data={
        'gampc': ['*.ui', 'plugins/*.ui', 'plugins/*.plugin', 'locale/messages.pot', 'locale/*/LC_MESSAGES/*.po'],
    },
    scripts=['bin/gampc', 'bin/gampc-module'],
    install_requires=['ampd', 'apsw', 'gbulb', 'xdg'],
    cmdclass={'compile_catalog': babel.compile_catalog,
              'extract_messages': babel.extract_messages,
              'init_catalog': babel.init_catalog,
              'update_catalog': babel.update_catalog},
)

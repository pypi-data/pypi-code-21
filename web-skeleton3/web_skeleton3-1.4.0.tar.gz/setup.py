# -*- encoding: utf-8 -*-

import os
import sys

from setuptools import setup, find_packages

if sys.version_info[:2] < (3, 5):
   raise RuntimeError('Requires Python 3.5 or better')

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

from web_skeleton import __version__

requires = [
    'yuicompressor',
    'mako',
    'webassets',
    'delegator',
]

setup(
    name='web_skeleton3',
    version=__version__,
    description='Static html code generator.',
    long_description=README + '\n\n',  # + CHANGES,
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
    ],
    author='ginsmar',
    author_email='niyamaka@yuneta.io',
    url='https://yuneta.io/web-skeleton',
    license='MIT License',
    keywords='html static generator mako webassets scss sass compass yuneta',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=[],
    entry_points="""\
        [console_scripts]
        web-skeleton3 = web_skeleton.main:main
    """,
)

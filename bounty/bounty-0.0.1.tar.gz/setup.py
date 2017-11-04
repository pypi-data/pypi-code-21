"""setup.py

.. codeauthor:: John Lane <john.lane93@gmail.com>

"""

from setuptools import setup
from bounty import __author__, __email__, __license__, __version__


setup(name='bounty',
      version=__version__,
      description='',
      author=__author__,
      author_email=__email__,
      url=u'https://github.com/jlane9/bounty',
      packages=['bounty'],
      install_requires=[],
      keywords='',
      license=__license__,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Operating System :: POSIX',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: MacOS :: MacOS X',
          'Topic :: Software Development :: Libraries',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6',
      ])

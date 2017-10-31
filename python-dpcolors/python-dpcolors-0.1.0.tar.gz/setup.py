from setuptools import setup, find_packages


setup(name='python-dpcolors',
      version='0.1.0',
      description='library to convert Xonotic color strings to various other formats',
      long_description=open('README.md').read(),
      url='https://github.com/nsavch/python-dpcolors',
      author='Nick Savchenko',
      author_email='nsavch@gmail.com',
      license='GPLv3',
      packages=find_packages(),
      keywords='xonotic',
      install_requires=[
          'setuptools',
          'ansicolors'
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'Intended Audience :: Developers',
          'Intended Audience :: Other Audience',  # gamers
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Software Development :: Libraries',
          'Topic :: Games/Entertainment',
      ],
)

import os
from setuptools import setup, find_packages, Command


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


setup(name='hydrophis',

      version='1.0.1',

      url='https://github.com/dpcrarchydrophis/hydrophis.git',

      license='meituan',

      author='dpcrarchydrophis',

      author_email='dpcrarchydrophis@gmail.com',

      description='python general crawler',

      packages=find_packages(exclude=['test', 'browser']),

      long_description=open('README.md').read(),

      zip_safe=False,

      install_requires=['nose', 'Twisted==17.1.0', 'beautifulsoup4', 'futures==3.1.1',
                        'gevent', 'requests==2.13.0', 'pybloom', 'boto==2.47.0', 'incremental==16.10.1',
                        'lxml==4.0.0', 'boto>=2.47.0'],

      test_suite='nose.collector',
      cmdclass={
        'clean': CleanCommand,
      })


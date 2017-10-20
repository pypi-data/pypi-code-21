#!/usr/bin/env python

from setuptools import setup

setup(name='deployment-director',
      version='0.1.6',
      description='Deployment Director',
      url='https://github.com/ushahidi/deployment-director',
      author='Ushahidi Team',
      author_email='team@ushahidi.com',
      license='MIT',
      packages=['DeploymentDirector', 'DeploymentDirector.actions'],
      package_dir = {'': 'src'},
      entry_points={'console_scripts':
                        ['deployment-director=DeploymentDirector.cli:main']},
      install_requires=['PyYAML>3', 'click>6', 'voluptuous>0.10', 'executor>=18', 'frozendict>=1.2'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      download_url='https://github.com/ushahidi/deployment-director/archive/0.1.6.tar.gz',
      keywords=['deploy', 'automation', ])

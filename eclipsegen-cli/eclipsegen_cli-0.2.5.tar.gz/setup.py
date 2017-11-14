from setuptools import setup

dependencies = [
  'eclipsegen==0.2.5', 'plumbum>=1.6.2'
]

setup(
  name='eclipsegen_cli',
  version='0.2.5',
  description='Generate Eclipse instances from a single command-line call',
  url='http://github.com/Gohla/eclipsegen_cli',
  author='Gabriel Konat',
  author_email='gabrielkonat@gmail.com',
  license='Apache 2.0',
  packages=['eclipsegen_cli'],
  install_requires=dependencies,
  test_suite='nose.collector',
  tests_require=['nose>=1.3.7'] + dependencies,
  entry_points={
    'console_scripts': [
      'eclipsegen = eclipsegen_cli.main:main'
    ],
  }
)

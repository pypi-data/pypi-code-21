import os.path

from setuptools import setup, find_packages


def abs_path(*paths):
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(here, *paths)


def version():
    v = {}
    with open(abs_path('fizzgun', '__init__.py')) as fp:
        exec(fp.read(), v)
    return v['__version__']


setup(name='fizzgun',
      version=version(),
      description='Fizzgun - Simple & Effective HTTP(S) Fuzzer',
      url='https://bitbucket.org/atlassian/fizzgun/',
      author='Sebastian Tello',
      author_email='stello@atlassian.com',
      packages=find_packages(exclude=('tests', 'tests.*', 'scripts', 'scripts.*')),
      include_package_data=True,
      install_requires=[
          'mitmproxy', 'pystache', 'pyzmq', 'pyyaml', 'requests'
      ],
      entry_points={
          'console_scripts': [
            'fizzgun=fizzgun.bin.cli:main'
          ]
      },
      zip_safe=False,
      license='Apache 2.0',
      classifiers=[
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7'
        ]
)

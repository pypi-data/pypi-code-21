import sys
from setuptools import setup
#from distutils.core import setup
from setuptools.command.test import test as TestCommand

readme = open('README.rst').read()
history = open('HISTORY.rst').read()


def parse_requirements():
    with open('requirements.txt') as req:
        return req.readlines()


class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)


setup(name='flotsam',
      version='0.1.2',
      description='Miscellaneous utilities',
      long_description=readme + '\n\n' + history,
      author='Bernhard (Bernd) Biskup',
      author_email='bbiskup@gmx.de',
      url='https://github.com/bbiskup',
      package_dir={'flotsam': 'flotsam'},
      packages=['flotsam'],
      zip_safe=False,
      include_package_data=True,
      install_requires=parse_requirements(),
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          # Topic :: Software Development :: Libraries :: Python Modules',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
      ],
      license='The MIT License (MIT)',
      keywords='flotsam utilities',
      tests_require=['tox'],
      cmdclass={'test': Tox}
      )

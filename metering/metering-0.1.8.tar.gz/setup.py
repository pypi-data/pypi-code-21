from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

# setup(name='metering',
#       description='Under development.',
#       url='https://bitbucket.org/arijackson/metering',
#       download_url='https://bitbucket.org/arijackson/metering/downloads',
#       author='Ari Jackson',
#       author_email='ari.j.jackson@gmail.com',
#       license='MIT',
#       version='0.0.46',
#       packages=['metering'],
#       test_suite='nose.collector',
#       tests_require=['nose'],
#       scripts=['bin/test-script'],
#       entry_points={'console_scripts':
#                     ['test-script=metering.command_line:main'], },
#       include_package_data=True,
#       zip_safe=False
#       )

setup(name='metering',
      description='Under development.',
      url='',
      download_url='',
      author='c__mite',
      author_email='',
      license='none',
      version='0.1.8',
      packages=['metering'],
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=['bin/test-script'],
      entry_points={'console_scripts':
                    ['test-script=metering.command_line:main'], },
      include_package_data=True,
      zip_safe=False
      )

# To publish to pypi: $ python setup.py sdist bdist_wheel
#                     $ twine upload dist/metering-0.0.XX.tar.gz
#                     $ pip install metering -U

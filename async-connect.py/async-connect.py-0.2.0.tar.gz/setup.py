import re
import sys

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

with open('async_connect/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

with open('README.rst') as f:
    readme = f.read()

if sys.version_info[1] == 6:
    test_require = ['uvloop>=0.8.1', 'ujson>=1.35']
else:
    test_require = ['ujson>=1.35']

setup(name='async-connect.py',
      author='GiovanniMCMXCIX',
      author_email='irimea.giovani.9@gmail.com',
      url='https://github.com/GiovanniMCMXCIX/async-connect.py',
      version=version,
      packages=find_packages(),
      license='MIT',
      description='Asynchronous version of connect.py',
      long_description=readme,
      include_package_data=True,
      python_requires='>=3.6.2',
      install_requires=requirements,
      extras_require={'performance': ['uvloop>=0.8.0', 'ujson>=1.35']},
      test_suite='tests',
      tests_require=test_require,
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.6',
          'Topic :: Internet',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
      ]
      )

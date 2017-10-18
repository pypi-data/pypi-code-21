# from setuptools import setup
from distutils.core import setup

from setuptools import find_packages

PACKAGE_NAME = "es_wrapper"

# packages = [
#   PACKAGE_NAME,
#   ]
packages = find_packages()

install_requires = ['elasticsearch',
                    'jsonpickle',
                    "pytz",
                    "logstash_formatter",
                    "jsonschema",
                    "isodate",
                    "six",
]

long_desc = """A wrapper for Elasticsearch"""

import es_wrapper
version = es_wrapper.__version__

setup(name=PACKAGE_NAME,
      version=version,
      description="A wrapper package for easy Elasticsearch Interface",
      long_description=long_desc,
      author="Guy Eshet",
      author_email="guyeshet@gmail.com",
      url="https://github.com/guyeshet/es_wrapper_package.git",
      install_requires=install_requires,
      packages=packages,
      package_data={},
      license="Apache 2.0",
      keywords="elasticsearch",
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: POSIX',
                   'Topic :: Internet :: WWW/HTTP'])

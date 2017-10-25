from setuptools import setup,find_packages
import sys
import datetime

PROJECT_VERSION = '3.7.9-SNAPSHOT'
PROJECT_NIGHTLY_VERSION = '3.7.9.dev'
# Note that the nightly version will have the executation date attached to the end of the version string
PROJECT_NAME = 'uforge_python_sdk'


# If we receive the "--nightly" parameter, we modify the version and name metadata

if "--nightly" in sys.argv:
    project_version = PROJECT_NIGHTLY_VERSION + datetime.date.today().strftime("%Y%m%d")
    print "Nightly version:" + project_version
    sys.argv.remove("--nightly")
else:
    project_version = PROJECT_VERSION
    print "Stable version:" + project_version

setup (

  # Declare your packages' dependencies here, for eg:
  install_requires=[
      'lxml==3.3.5',
      'pyxb==1.2.4',
      'requests==2.13.0'
  ],
  package_data={'uforge': ['config/*',]},

  name = PROJECT_NAME,
  version = project_version,
  packages = find_packages(),

  description='UForge python SDK',
  long_description='',
  author = 'UShareSoft',
  author_email = 'contact@usharesoft.com',
  license="Apache License 2.0",
  url = '',
  classifiers=(
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)

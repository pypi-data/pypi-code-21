import os.path
from setuptools import setup, find_packages


# single source of truth for package version
version_ns = {}
with open(os.path.join("globus_sdk", "version.py")) as f:
    exec(f.read(), version_ns)

setup(name="globus-sdk",
      version=version_ns["__version__"],
      description="Globus SDK for Python",
      long_description=open("README.rst").read(),
      author="Globus Team",
      author_email="support@globus.org",
      url="https://github.com/globus/globus-sdk-python",
      packages=find_packages(exclude=['tests', 'tests.*']),
      install_requires=[
          'requests>=2.0.0,<3.0.0',
          'six>=1.10.0,<2.0.0'
      ],

      extras_require={
          'jwt': ['pyjwt[crypto]>=1.5.3,<2.0.0']
      },

      include_package_data=True,

      keywords=["globus", "file transfer"],
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Apache Software License",
          "Operating System :: MacOS :: MacOS X",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: POSIX",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Topic :: Communications :: File Sharing",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      )

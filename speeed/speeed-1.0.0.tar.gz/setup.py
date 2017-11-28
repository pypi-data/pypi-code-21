#!/usr/bin/env python3

from setuptools import setup


def readme():
    with open("README.md") as fd:
        return fd.read()


setup(name="speeed",
      version="1.0.0",
      description="Ping like tool that measures packet speed instead of response time",
      author="Ricardo Band",
      author_email="email@ricardo.band",
      url="https://github.com/XenGi/speeed",
      long_description=readme(),
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "Intended Audience :: End Users/Desktop",
          "Intended Audience :: System Administrators",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3 :: Only",
          "Topic :: Internet",
          "Topic :: Scientific/Engineering :: Visualization",
          "Topic :: System :: Networking",
          "Topic :: Utilities"],
      keywords=["ping", "traceroute", "speed", "speedtest"],
      license="MIT",
      packages=["speeed", ],
      entry_points = {'console_scripts': ['speeed=speeed.speeed:cli'], },
      install_requires=["requests", "docopt"],
      python_requires='>=3',
     )


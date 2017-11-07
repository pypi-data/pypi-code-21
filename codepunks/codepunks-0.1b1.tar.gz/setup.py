import os
import runpy

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.md')).read()


tests_require = [
    'pytest',
    'pytest-cov',
    'pytest-runner',
]

# Extract the version from codepunks
VERSION = runpy.run_path(os.path.join(here, "codepunks/version.py"))["VERSION"]


def requirements(filename):
    if os.path.exists(filename):
        return [l for l in open(filename).read().splitlines()
                    if not l.startswith("#")]
    else:
        return ""


setup(name='codepunks',
      version=VERSION,
      description='Codepunks, yet another base library',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Intended Audience :: Developers",
          "Operating System :: POSIX",
          "Natural Language :: English",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Development Status :: 3 - Alpha",
          ],
      author='Chris Newton',
      author_email='redshodan@gmail.com',
      url='https://github.com/redshodan/codepunks',
      keywords=[],
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      platforms=["Any"],
      test_suite='codepunks',
      install_requires=requirements("requirements.txt"),
      setup_requires=['pytest-runner'],
      tests_require=tests_require,
      license="Apache Software License",
      )

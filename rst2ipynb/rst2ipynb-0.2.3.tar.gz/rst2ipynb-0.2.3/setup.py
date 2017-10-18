## -*- encoding: utf-8 -*-
"""
reST to Jupyter notebook converter
"""

# Always prefer setuptools over distutils
from setuptools import setup
from setuptools.command.install import install
from distutils.errors import DistutilsExecError
# To use a consistent encoding
from codecs import open
import os


here = os.path.dirname(__file__)

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


class check_install(install):
    "Check that pandoc is installed on the system"
    def run(self):
        import subprocess
        try:
            # Hide stdout but allow stderr
            subprocess.check_call(["pandoc", "-v"], stdout=open(os.devnull))
        except subprocess.CalledProcessError:
            raise DistutilsExecError("rst2ipynb requires the Haskell program 'pandoc'. It seems to be installed, but it did not work properly.")
        except OSError:
            raise DistutilsExecError("rst2ipynb requires the Haskell program 'pandoc'. You need to install it on your system.")
        install.run(self)


setup(
    name='rst2ipynb',
    version='0.2.3',
    description='A reST to Jupyter notebook converter',
    long_description=long_description,
    url='https://github.com/nthiery/rst-to-ipynb',
    author='Scott Sievert, Nicolas M. Thiéry',
    author_email='nthiery@users.sf.net',
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],
    scripts=["rst2ipynb", "rst2ipynb-sageblock-filter"],
    install_requires=['notedown', 'pandocfilters'],
    #setup_requires=['pytest-runner'],
    #tests_require=['pytest'],
    cmdclass=dict(install=check_install)
)

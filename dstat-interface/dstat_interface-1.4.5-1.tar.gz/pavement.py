import sys

from paver.easy import task, needs, path, sh, cmdopts, options
from paver.setuputils import setup, install_distutils_tasks, find_packages
from distutils.extension import Extension
from distutils.dep_util import newer

sys.path.insert(0, path('.').abspath())
import version

setup(name='dstat_interface',
      version=version.getVersion(),
      description='Interface software for DStat potentiostat.',
      keywords='',
      author='Michael D. M Dryden',
      author_email='mdryden@chem.utoronto.ca',
      url='http://microfluidics.utoronto.ca/dstat',
      license='GPLv3',
      packages=find_packages(),
      install_requires=['matplotlib', 'numpy', 'pyserial', 'pyzmq',
                        'pyyaml','seaborn', 'setuptools', 
                        'zmq-plugin>=0.2.post2'],
      # Install data listed in `MANIFEST.in`
      include_package_data=True)


@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass

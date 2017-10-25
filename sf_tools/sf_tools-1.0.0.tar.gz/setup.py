from setuptools import setup, find_packages
from sf_tools import __version__

setup(
    name='sf_tools',
    author='sfarrens',
    author_email='samuel.farrens@gmail.com',
    version=__version__,
    url='https://github.com/sfarrens/sf_tools',
    download_url='https://github.com/sfarrens/sf_tools/archive/0.1.tar.gz',
    packages=find_packages(),
    license='MIT',
    long_description=open('README.txt').read(),
)

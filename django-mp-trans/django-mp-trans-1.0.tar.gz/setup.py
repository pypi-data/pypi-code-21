
from setuptools import setup, find_packages

from trans import __version__


with open('requirements.txt') as f:
    install_requires = f.read().splitlines()


url = 'https://github.com/pmaigutyak/mp-trans'


setup(
    name='django-mp-trans',
    version=__version__,
    description='Django trans apps',
    long_description=open('README.md').read(),
    author='Paul Maigutyak',
    author_email='pmaigutyak@gmail.com',
    url=url,
    download_url='%s/archive/%s.tar.gz' % (url, __version__),
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    install_requires=install_requires
)

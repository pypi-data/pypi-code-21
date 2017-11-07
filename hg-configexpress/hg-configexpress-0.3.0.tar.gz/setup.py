#coding: utf8
from distutils.core import setup

setup(
    name='hg-configexpress',
    version='0.3.0',
    author='Mathias de Maré',
    author_email='mathias.demare@gmail.com',
    maintainer='Pierre-Yves David',
    maintainer_email='pierre-yves.david@ens-lyon.org',
    url='https://bitbucket.org/Mathiasdm/hg-configexpress',
    description=('Mercurial extension to monitor and enforce client configuration'),
    long_description=open('README').read(),
    keywords='hg mercurial',
    license='GPLv2+',
    packages=['hgext3rd'],
)

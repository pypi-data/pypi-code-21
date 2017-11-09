import setuptools
from distutils.core import setup

setup(
    name='ohadlibs',
    packages=setuptools.find_packages(),  # this must be the same as the name above
    version='0.1.2',
    description='A set of tools that I created for my personal work. I use them on a daily basis so I organized them inside a library. The library should get updated frequently.',
    author='Ohad Chaet',
    author_email='ohadch9518@gmail.com',
    url='https://github.com/ohadch/ohadlibs',  # use the URL to the github repo
    download_url='https://github.com/peterldowns/mypackage/archive/0.1.tar.gz',  # I'll explain this in a second
    keywords=[],  # arbitrary keywords
    classifiers=['Programming Language :: Python :: 2.7'],
    install_requires=['cloudshell-automation-api'],
    python_requires='<3'
)

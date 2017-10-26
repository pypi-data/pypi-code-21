from setuptools import setup, find_packages
import os

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

__version__ = None
name = 'ahqapiclient'
here = os.path.abspath(os.path.dirname(__file__))

with open('%s/requirements.txt' % here) as f:
    requires = f.readlines()

with open('%s/version.txt' % here) as f:
    __version__ = f.readline().strip()

setup(
    name=name,
    version=__version__,
    description='AbuseHQ API Client',
    long_description=long_description,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords='abusehq api client',
    author='Frederik Petersen',
    author_email='fp@abusix.com',
    url='https://www.abusix.com/',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
)

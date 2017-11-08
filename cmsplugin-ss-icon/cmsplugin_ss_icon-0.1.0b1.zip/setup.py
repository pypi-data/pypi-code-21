from setuptools import setup, find_packages
from codecs import open
from os import path
import cmsplugin_ss_icon

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cmsplugin_ss_icon',
    version=cmsplugin_ss_icon.__version__,

    description='Add support for font awesome icons to django cms',
    long_description=long_description,

    url='https://github.com/alexjbartlett/djangocms-ss-icon',

    # Author details
    author='Alex J Bartlett',
    author_email='alex@sourceshaper.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='djangocms fontawesome',

    packages=find_packages(),
    include_package_data=True,

    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    # install_requires=['django-cms>3.0,<=3.4.4',],

)

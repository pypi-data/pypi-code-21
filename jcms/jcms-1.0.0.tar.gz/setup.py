from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='jcms',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='1.0.0',

    description='This is a cms written in Django and made by JCB Development',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/jessielaf/jcms',

    # Author details
    author='Jessie Liauw A Fong',
    author_email='jessielaff@live.nl',

    # Choose your license
    license='MIT',

    # See https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Site Management',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.4',
        'Framework :: Django :: 1.11'
    ],

    # What does your project relate to?
    keywords='cms admin development content management system',

    packages=find_packages(),

    package_data={
        'static': [
            'jcms.app.bundle.js',
            'jcsm.dropdown.js',
            'jcms.style.css',
            'jcms.grid.css'
        ],
        'templates': {
            'icons': [
                'detail.html',
                'edit_or_create.html',
                'forms.html',
                'list.html'
            ],
            'jcms-admin': {
                'crud': [
                    'detail.html',
                    'edit_or_create.html',
                    'forms.html',
                    'list.html'
                ],
                'layouts': [
                    'admin.html',
                    'base.html',
                    'messages.html',
                    'side-nav.html',
                    'top.html'
                ],
                'login': {
                    'login.html'
                }
            },
            'README.md': ''
        }
    }

)

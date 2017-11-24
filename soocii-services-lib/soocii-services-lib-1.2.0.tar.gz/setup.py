# Sample https://github.com/pypa/sampleproject

from setuptools import setup, find_packages

setup(
    name='soocii-services-lib',
    version='1.2.0',
    packages=find_packages(exclude=['tests']),
    url='https://github.com/drmobile/services-lib',
    license='Apache Software License',
    author='Soocii',
    author_email='service@soocii.me',
    description='Library for Soocii back-end services which include common functions/scripts/packages.',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['click', 'Fabric3', 'boto3', 'awscli', 'pycrypto', 'flask'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'test': ['pytest', 'tox'],
        'doc': ['Sphinx']
    }
)

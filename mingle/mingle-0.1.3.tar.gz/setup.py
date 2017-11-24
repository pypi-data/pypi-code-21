from setuptools import setup

__version__ = "0.1.3"   # Ensure this matches mingle.__version__ and tags are pushed!!


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='mingle',
    version=__version__,
    description='Get lines from a number of log files with different time-stamp formats in chronological order',
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: System :: Logging',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Indexing',
        'Topic :: Utilities',
    ],
    keywords='',
    url='https://bitbucket.org/swbclarke/mingle',
    download_url='https://bitbucket.org/swbclarke/mingle/get/{}.tar.gz'.format(__version__),
    author='Sebastian Clarke',
    author_email='swb@rift.team',
    license='MIT',
    packages=['mingle'],
    install_requires=[
      'python-dateutil',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    entry_points={
        'console_scripts': ['mingle=mingle.command:main'],
    },
    include_package_data=True,
    zip_safe=False
)
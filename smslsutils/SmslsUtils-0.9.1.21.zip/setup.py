from setuptools import setup, find_packages
import version

setup(
    name='SmslsUtils',
    version='{0}.{1}.{2}.{3}'.format(version.MAJOR, version.MINOR, version.PATCH, version.BUILD),
    description='This package provides utility functions for working with ARGEN/SMSLS data and systems.',
    url='https://bitbucket.org/apmtinc/smslsutils',
    author='Fluence Analytics',
    author_email='watson.boyett@fluenceanalytics.com',
    license='GNU GPL v3',
    keywords='ARGEN SMSLS Fluence',
    packages=[
        'SmslsUtils.DataTools', 
        'SmslsUtils.SmslsDevicePy', 
        'SmslsUtils.SmslsTron', 
        'SmslsUtils.MalsRecorder'],
    install_requires=['pandas','numpy','matplotlib'],
    package_data={'': ['*.dll', '*.pyd']},
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Win32 (MS Windows)',
        'Operating System :: Microsoft :: Windows',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities'
    ],
    zip_safe=False
)

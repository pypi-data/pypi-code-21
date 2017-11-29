from setuptools import setup, find_packages

# version numbers follow SemVer
VER_MAJOR = 0  # bump MAJOR version when breaking changes are introduced to the API
VER_MINOR = 9  # bump MINOR version when new features (non-breaking) are introduced
VER_PATCH = 2  # bump PATCH version when only bug-fixes are introduced (no new features)
VER_BUILD = 24  # BUILD version is automatically incremented by the build server 


setup(
    name='SmslsUtils',
    version='{0}.{1}.{2}.{3}'.format(VER_MAJOR, VER_MINOR, VER_PATCH, VER_BUILD),
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

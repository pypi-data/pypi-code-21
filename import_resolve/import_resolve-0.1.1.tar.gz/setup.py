"""
Resolves pip imports in a python project
"""
from setuptools import setup

dependencies = ['argparse']

setup(
    name='import_resolve',
    version='0.1.1',
    url='https://github.com/PandaWhoCodes/import_resolve',
    license='MIT',
    author='Thomas Ashish Cherian',
    author_email='ufoundashish@gmail.com',
    description='Resolves pip imports in a python project',
    long_description=__doc__,
    packages=['import_resolve'],
    include_package_data=True,
    zip_safe=True,
    platforms='any',
    scripts=['import_resolve/check.py'],
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'import_resolve = import_resolve.check:argParser',
        ],
    },

    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

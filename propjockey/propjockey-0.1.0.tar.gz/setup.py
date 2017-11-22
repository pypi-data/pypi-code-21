import os

from setuptools import setup, find_packages

module_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name='propjockey',
    version='0.1.0',
    description='Spinning property workflows. Taking requests.',
    long_description=open(os.path.join(module_dir, 'README.md')).read(),
    url='https://github.com/materialsproject/propjockey',
    author='MP team',
    author_email='matproj-develop@googlegroups.com',
    license='modified BSD',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'pymongo',
        'requests',
        'toolz',
    ],
    extras_require={"prod_matsci": ["gunicorn", "pymatgen"]},
    classifiers=["Programming Language :: Python :: 2",
                 "Programming Language :: Python :: 2.7",
                 'Development Status :: 2 - Pre-Alpha',
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: System Administrators',
                 'Intended Audience :: Information Technology',
                 'Operating System :: OS Independent',
                 'Topic :: Other/Nonlisted Topic',
                 'Topic :: Database :: Front-Ends',
                 'Topic :: Scientific/Engineering'],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)

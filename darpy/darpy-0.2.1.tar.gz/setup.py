import os
from setuptools import setup, find_packages

with open('README.rst', 'r') as f:
    readme_text = f.read()

# single source of truth for package version
version_ns = {}
with open(os.path.join("darpy", "version.py")) as f:
    exec(f.read(), version_ns)
version = version_ns['__version__']

setup(
    name='darpy',
    version=version,

    packages=find_packages(),
    entry_points={'console_scripts': ['darpy = darpy.main:main']},

    description='Distribute ARchived PYthon',
    long_description=readme_text,
    author='Stephen Rosen',
    author_email='sirosen@globus.org',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: Apache Software License',
        'Environment :: Console'
    ]
)

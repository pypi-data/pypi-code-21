from setuptools import setup
from setuptools import find_packages
from distutils.extension import Extension

try:
    from Cython.Build import cythonize
except ImportError:
    def cythonize(extensions): return extensions
    sources = ['rocksdb_iota/_rocksdb.cpp']
else:
    sources = ['rocksdb_iota/_rocksdb.pyx']

mod1 = Extension(
    'rocksdb_iota._rocksdb',
    sources,
    extra_compile_args=[
        '-std=c++11',
        '-O3',
        '-Wall',
        '-Wextra',
        '-Wconversion',
        '-fno-strict-aliasing',
        '-Iinclude'
    ],
    language='c++',
    libraries=[
        'rocksdb',
        'snappy',
        'bz2',
        'z'
    ]
)

setup(
    name="python-rocksdb-iota",
    version='0.7.1',
    description="Python bindings for RocksDB with IOTA modification",
    long_description=open('README.rst', 'r').read(),
    keywords='rocksdb, IOTA',
    author='Louie Lu',
    author_email="git@louie.lu",
    url="https://github.com/mlouielu/python-rocksdb",
    license='BSD License',
    install_requires=['setuptools'],
    package_dir={'rocksdb_iota': 'rocksdb_iota'},
    packages=find_packages('.'),
    ext_modules=cythonize([mod1]),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only'
    ]
)

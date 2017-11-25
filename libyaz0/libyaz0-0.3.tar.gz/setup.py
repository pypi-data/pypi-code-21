from setuptools import setup

setup(
    name = 'libyaz0',
    packages = ['libyaz0'],
    version = '0.3',
    description = 'A library for compressing/decompressing Yaz0/1 compression formats',
    author = 'AboodXD',
    author_email = 'aboood40091@gmail.com',
    url = 'https://github.com/aboood40091/libyaz0',
    download_url = 'https://github.com/aboood40091/libyaz0/archive/v0.3.tar.gz',
    keywords = ['compress', 'decompress', 'yaz0', 'szs', 'yaz1'],
    license = 'GNU General Public License v3 (GPLv3)',
    include_package_data=True,
    classifiers = [
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Cython',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Archiving :: Compression',
    ],
)

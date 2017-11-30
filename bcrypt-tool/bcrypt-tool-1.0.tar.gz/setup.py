from setuptools import setup

setup(
    name='bcrypt-tool',
    packages=['bcrypt_tool'],
    version='1.0',
    description = 'CLI tool for creating and matching bcrypt hashes',
    author='Dmitri Smirnov',
    author_email='dmitri@smirnov.ee',
    py_modules=['sys', 'bcrypt', 'Click'],
    LICENSE = 'Apache License 2.0',
    url = 'https://github.com/smirnov/bcrypt_tool',
    download_url='https://github.com/smirnov/bcrypt_tool/archive/1.0.tar.gz',
    install_requires=[
        'Click',
        'bcrypt',
    ],
    entry_points={
        'console_scripts': [
            'bcrypt-tool = bcrypt_tool.main:cli '
        ],
    },
)

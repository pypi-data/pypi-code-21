from setuptools import setup

setup(
    name='rarbg',
    version='1.1.2',
    description='RSS interface to TorrentAPI',
    url='https://github.com/banteg/rarbg',
    py_modules=['rarbg'],
    install_requires=[
        'aiohttp',
        'python-dateutil',
        'humanize',
        'jinja2',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'rarbg = rarbg:main',
        ],
    }
)

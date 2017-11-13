from pathlib import Path

from setuptools import setup, find_packages

try:
    from golgi.config.write import write_pkg_config
except ImportError:
    conf = []  # type: ignore
else:
    write_pkg_config('.', Path('tek_utils.conf'), 'tek_utils')
    write_pkg_config('.', Path('sharehoster.conf'), 'sharehoster')
    conf = ['tek_utils.conf', 'sharehoster.conf']

version_parts = (3, 8, 1)
version = '.'.join(map(str, version_parts))

setup(
    name='tek_utils',
    version=version,
    packages=find_packages(exclude=['tests', 'tests.*']),
    data_files=[('share/tek_utils/config', conf)],
    install_requires=[
        'requests',
        'amino>=10.1.0',
        'golgi>=1.7.0',
        'tek>=3.0.0',
        'lxml',
        'ThePirateBay',
        'pyquery',
        'cfscrape',
    ],
    entry_points={
        'console_scripts': [
            'iptabler = tek_utils.iptables:iptabler',
            'extract = tek_utils.extract:extract',
            'shget = tek_utils.sharehoster:shget',
            'tget = tek_utils.sharehoster:tget',
            'sh_release = tek_utils.sharehoster.search:sh_release',
            'gain_collection = tek_utils.gain:gain_collection',
            'process_album = tek_utils.process_album:process_album',
        ]
    }
)

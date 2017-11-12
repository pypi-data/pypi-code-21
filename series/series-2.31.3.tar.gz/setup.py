from pathlib import Path

from setuptools import setup, find_packages

version_parts = (2, 31, 3)
version = '.'.join(map(str, version_parts))

try:
    from golgi.config.write import write_pkg_config
except ImportError:
    conf = []  # type: ignore
else:
    write_pkg_config('.', Path('series.conf'), 'series')
    conf = ['series.conf']

setup(
    name='series',
    version=version,
    author='Torsten Schmits',
    author_email='torstenschmits@gmail.com',
    license='GPLv3',
    packages=find_packages(exclude=['integration', 'integration.*', 'unit',
                                    'unit.*']),
    data_files=[('share/series/config', conf)],
    package_data={
        '': ['alembic/env.py', 'alembic.ini', 'alembic/versions/*.py'],
    },
    install_requires=[
        'amino~=12.3.0',
        'golgi~=1.9.3',
        'tek-utils>=3.7.0',
        'requests',
        'sqlpharmacy',
        'crystalmethod',
        'lxml',
        'feedparser',
        'flask',
        'alembic',
        'tvrampage',
        'python-dateutil',
        'guessit',
    ],
    entry_points={
        'console_scripts': [
            'serieslibd = series.library.cli:libd',
            'serieslibc = series.library.cli:libc',
            'seriesgetd = series.get.cli:getd',
            'seriesgetc = series.get.cli:getc',
            'subsync_dir = series.subsync:subsync_dir_cli',
            'subsync_cwd = series.subsync:subsync_cwd',
            'subsync_auto = series.subsync:subsync_auto',
            'handle_episode = series.handle_episode:handle_episode_cli',
            'store_episode = series.store_episode:store_episode_cli',
        ]
    }
)

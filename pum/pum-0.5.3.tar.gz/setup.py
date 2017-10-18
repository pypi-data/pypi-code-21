from setuptools import setup

setup(
    name = 'pum',
    packages = ['pum', 'pum/core', 'pum/utils'],
    scripts = ['scripts/pum'],
    version = '0.5.3',
    description = 'Postgres upgrade manager',
    author = 'Mario Baranzini',
    author_email = 'mario@opengis.ch',
    url = 'https://github.com/opengisch/pum',
    download_url = 'https://github.com/opengisch/pum/archive/0.5.3.tar.gz', # I'll explain this in a second
    keywords = ['postgres', 'migration', 'upgrade'],
    classifiers = [],
    install_requires=['psycopg2 (>=2.7.3)'],
)

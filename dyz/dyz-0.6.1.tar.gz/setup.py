import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = '0.6.1'

setup(
    name='dyz',
    version=version,
    description="dyz",
    long_description=README,
    classifiers=[
    ],
    keywords='dyz',
    author='me',
    author_email='me@example.org',
    url='https://example.org',
    license='LGPL v3',
    py_modules=['dyz'],
    include_package_data=True,
    install_requires=[
        'click',
        'odoorpc',
        'prettytable',
        'ConfigParser',
        'XlsxWriter',
        'lxml',
        'pyyaml',
        'validictory',
        'python-dateutil',
        'dyools',
        'psycopg2',
    ],
    entry_points='''
        [console_scripts]
        dyz=dyz:main
    ''',
)

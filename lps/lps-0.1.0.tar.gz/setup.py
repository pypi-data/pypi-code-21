import os
from setuptools import setup


def filter_requirements(fn):
    with open(fn) as fh:
        filtered_requirements = []
        for line in fh.readlines():
            if line[0] in ['#', ' ', '-']:
                continue
            filtered_requirements.append(line)
    return filtered_requirements


def load_version():
    with open('VERSION') as fh:
        res = fh.read()
    return res


version = load_version()

required = filter_requirements('requirements.txt')

required_test = filter_requirements('requirements-test.txt')

long_description = 'Script to lay out a large print job on multiple pages with alignment marks'

if os.path.exists('README.rst'):
    with open('README.rst') as fh:
        long_description = fh.read()

setup(
    name='lps',
    description='Lay out large print jobs as PDFs with alignment marks.',
    long_description=long_description,
    version=version,
    author='Chris Speck',
    author_email='cgspeck@gmail.com',
    url='https://github.com/cgspeck/largeprintsplitter',
    packages=['lps'],
    install_requires=required,
    extras_require={
        'tests': required_test
    },
    entry_points='''
        [console_scripts]
        lps=lps.cli:run_cli
    ''',
    keywords=['print', 'printing', 'layout', 'pdf', 'plan', 'engineering', 'fabrication'],
    download_url=f'https://github.com/cgspeck/largeprintsplitter/archive/{version}.tar.gz'
)

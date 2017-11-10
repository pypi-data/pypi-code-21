from setuptools import setup, find_packages

setup(
    name='flextime',
    version='1.0',
    license='GPLv3',
    packages=['flextime'],
    description='Hierarchical task management tool',
    author='John Frederick Cornish IV',
    author_email='johncornishthe4th@gmail.com',
    url='https://github.com/johncornish/flextime',
    download_url='https://github.com/johncornish/flextime/archive/1.0.tar.gz',
    install_requires=[
        'click',
        'python-dateutil',
        'PyYAML',
        'networkx',
        'pytest',
    ],
    entry_points='''
    [console_scripts]
    ft=flextime:cli
    ''',
)

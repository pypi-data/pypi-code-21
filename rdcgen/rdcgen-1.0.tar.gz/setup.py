from setuptools import setup, find_packages

setup(
    name='rdcgen',
    packages=['rdcgen'],
    version='1.0',
    license='GPLv3',
    description='Generate RDCMan config files from Active Directory',
    author='John Frederick Cornish IV',
    author_email='johncornishthe4th@gmail.com',
    url='https://github.com/johncornish/RDCGen',
    download_url='https://github.com/johncornish/RDCGen/archive/1.0.tar.gz',
    install_requires=[
        'click',
        'ldap3',
        'PyYAML',
        'lxml',
    ],
    entry_points='''
    [console_scripts]
    rgen=rdcgen:cli
    ''',
)

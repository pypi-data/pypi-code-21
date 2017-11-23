""" IR-Flow Client setup.py"""

from setuptools import setup

with open('requirements.txt') as f:
    base_requirements = f.read().splitlines()

with open('requirements-dev.txt') as f:
    dev_requirements = f.read().splitlines()

setup(
    name='irflow_client',
    version=open('VERSION').read(),
    author='JP Bourget, Michael Deale',
    author_email='jp@syncurity.net',
    maintainer='Syncurity Corp.',
    maintainer_email='support@syncurity.net',
    description=open('SUMMARY').read(),
    keywords='Syncurity syncurity IR-Flow ir-flow irflow security incident response',
    long_description=open('DESCRIPTION').read(),
    license='Commercial',
    url='https://github.com/Syncurity/irflow-sdk-python',
    packages=['irflow_client'],
    install_requires=base_requirements,
    extras_requires={
        'dev': [
            dev_requirements
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Security',
    ]
)

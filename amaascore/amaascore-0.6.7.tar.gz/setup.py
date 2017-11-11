from setuptools import setup, find_packages

requires = [
    'amaasutils',
    'configparser',
    'python-dateutil',
    'pytz',
    'requests',
    'warrant'
]

setup(
    name='amaascore',
    version='0.6.7',
    description='Asset Management as a Service - Core SDK',
    license='Apache License 2.0',
    url='https://github.com/amaas-fintech/amaas-core-sdk-python',
    author='AMaaS',
    author_email='tech@amaas.com',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['tests']),  # Very annoying that this doesnt work - I have to include a MANIFEST
    install_requires=requires,
)

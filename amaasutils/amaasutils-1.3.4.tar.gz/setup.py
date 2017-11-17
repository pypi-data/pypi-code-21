from setuptools import setup, find_packages

requires = [
    'python-dateutil'
]

setup(
    name='amaasutils',
    version='1.3.4',
    description='Asset Management as a Service - Utils',
    license='Apache License 2.0',
    url='https://github.com/amaas-fintech/amaas-utils-python',
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

from setuptools import setup, find_packages

requires = [
    'python-dateutil',
    'workalendar',
    'pycountry'
]

setup(
    name='fincalendar',
    version='0.1.6',
    description='Finance Calendar',
    license='Apache License 2.0',
    url='https://github.com/amaas-fintech/fincalendar',
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

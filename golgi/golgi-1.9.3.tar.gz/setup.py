from setuptools import setup, find_packages

version_parts = (1, 9, 3)
version = '.'.join(map(str, version_parts))

setup(
    name='golgi',
    description='app config and execution tools',
    version=version,
    author='Torsten Schmits',
    author_email='torstenschmits@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['integration', 'integration.*', 'unit', 'unit.*']),
    install_requires=[
        'amino~=12.3.0',
    ],
    tests_require=[
        'kallikrein',
    ],
)

# coding=utf-8
from setuptools import setup, find_packages
setup(
    name='aiojsonflow',
    version='0.0.1',
    description='use json to program the flow of work steps, with async support.',
    long_description="Write scripts in JSON format and run it. Easy to extend it by writting simple python functions. It's a way to let user run custom scripts in a flow.",
    author='myrfy001',
    url='https://github.com/myrfy001/aiojsonflow',
    license='Apache',
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 1 - Planning',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 3.6',
    ],
    keywords='json programming async',
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=[],
    extras_require={},
    package_data={},
    data_files=[],
    entry_points={}
)

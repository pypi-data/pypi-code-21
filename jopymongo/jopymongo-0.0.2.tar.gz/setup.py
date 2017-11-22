from setuptools import setup

setup(
    name='jopymongo',
    version='0.0.2',
    packages=['jopymongo'],
    package_data={'jopymongo': ['*.jo']},
    python_requires='>=3',
    install_requires=[
        'jojo',
        'pymongo',
    ]
)

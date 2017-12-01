from setuptools import setup, find_packages

setup(
    name="secret_storage",
    version="0.0.1",
    author="David Ng",
    author_email="david.ng.dev@gmail.com",
    description=("Tools for extract sensitive configuration out of your project"),
    url="https://github.com/davidNHK/secret-storage",
    download_url="https://github.com/davidNHK/secret-storage/archive/v0.0.1.zip",
    license="BSD",
    packages=find_packages("./", exclude=["tests"]),
    keywords=['generic-storage', 'secret-data'],
    classifiers=[],
    install_requires=[
        'pylint',
        'pytest',
        'pytest-cov',
        'twine',
        'boto3'
    ]
)
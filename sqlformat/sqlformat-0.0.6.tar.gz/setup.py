from setuptools import setup, find_packages

setup(
    name="sqlformat",
    version="0.0.6",
    author="David Ng",
    author_email="david.ng.dev@gmail.com",
    description=("Tools for make SQL statement can accept argument and group together on run times"),
    url="https://github.com/davidNHK/sql-format",
    download_url="https://github.com/davidNHK/sql-format/archive/v0.0.6.zip",
    license="BSD",
    packages=find_packages("./", exclude=["tests"]),
    keywords=['sql', 'formatting', 'reporting'],
    classifiers=[],
    install_requires=[
        'pylint',
        'pytest',
        'pytest-cov',
        'twine'
    ]
)
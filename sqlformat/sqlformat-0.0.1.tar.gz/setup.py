from setuptools import setup

from pip.req import parse_requirements

setup(
    name="sqlformat",
    version="0.0.1",
    author="David Ng",
    author_email="david.ng.dev@gmail.com",
    description=("Tools for make SQL statement can accept argument and group together on run times"),
    url="https://github.com/davidNHK/sql-format",
    download_url="https://github.com/davidNHK/sql-format/archive/v0.0.1.zip",
    license="BSD",
    packages=['sqlformat'],
    keywords=['sql', 'formatting', 'reporting'],
    classifiers=[],
    install_requires=[
        str(r.req) for r in parse_requirements(
            "./requirements.txt",
            session='hack'  # What that?
        )
    ]
)
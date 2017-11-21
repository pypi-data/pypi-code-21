import sys
from pip.req import parse_requirements
from setuptools import setup, find_packages
install_reqs = parse_requirements('requirements.txt', session="setup")
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name="Logrdis",
    version_format="{tag}",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "*.pyc"]),
    include_package_data=True,
    package_data={'': ['requirements.txt']},
    install_requires=reqs,
    setup_requires=['setuptools>=8.0.0', 'setuptools-git-version'],
    entry_points={
        "console_scripts": [
            'logrdis = logrdis.core:run_log_server'
        ]
    },
    data_files=[(sys.prefix + '/etc/logrdis/logrdis.sample.yml', ['tests/test.yml'])],
    author="Matt Daue",
    author_email="mdaue@carbyne.solutions",
    description="A fully configurable stream redirector from a socket to a database",
    license="BSD-4-Clause",
    keywords="log stream sql redirect",
    url="https://github.com/Carbyne-Solutions/logrdis",
)
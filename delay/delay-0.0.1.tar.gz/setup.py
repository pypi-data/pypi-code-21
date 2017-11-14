import sys
from pip.req import parse_requirements
from setuptools import setup, find_packages
install_reqs = parse_requirements('requirements.txt', session="setup")
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name="delay",
    version_format="{tag}",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "*.pyc"]),
    include_package_data=True,
    package_data={'': ['requirements.txt']},
    install_requires=reqs,
    setup_requires=['setuptools>=8.0.0', 'setuptools-git-version'],
    data_files=[],
    author="Matt Daue",
    author_email="mdaue@carbyne.solutions",
    description="A micro library focused on providing wait states in distributed systems",
    license="BSD-3-Clause",
    keywords="sql key value database",
    url="https://github.com/Carbyne-Solutions/delay",
)

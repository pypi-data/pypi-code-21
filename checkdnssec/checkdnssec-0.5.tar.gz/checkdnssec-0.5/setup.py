"""Project setup."""

from subprocess import check_output

from setuptools import find_packages, setup


def version_from_git():
    """Acquire package version form current git tag."""
    return check_output(['git', 'describe', '--tags', '--abbrev=0'],
                        universal_newlines=True).strip()


setup(
    name='checkdnssec',
    version=version_from_git(),
    packages=find_packages(),
    description="Verify if domain names use DNSSEC.",
    long_description=open('README.md').read(),
    install_requires=[
        'dnspython',
        'pycrypto',
    ],
    entry_points={
        'console_scripts': [
            'checkdnssec = checkdnssec:main',
        ],
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)

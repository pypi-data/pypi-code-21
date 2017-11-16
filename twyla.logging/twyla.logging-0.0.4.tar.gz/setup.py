from setuptools import setup

dependencies = ['requests_futures']

setup(
    name="twyla.logging",
    version="0.0.4",
    author="Twyla Devs",
    author_email="dev@twylahelps.com",
    description=("Twyla Logging Utilities"),
    install_requires=dependencies,
    extras_require={
        'test': ['pytest'],
    },
    packages=["twyla.logging"],
    entry_points={},
    url="https://bitbucket.org/twyla/twyla.raml",
)

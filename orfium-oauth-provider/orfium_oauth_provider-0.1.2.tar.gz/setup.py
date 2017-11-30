from setuptools import setup

setup(
    # Application name:
    name="orfium_oauth_provider",

    # Version number (initial):
    version="0.1.2",

    # Application author details:
    author="Dimitris Papaspyros",
    author_email="dimitris@orfium.com",

    # Packages
    packages=["orfium_oauth_provider"],

    # Include additional files into the package
    package_data={'orfium_oauth_provider': ['*.html']},
    include_package_data=True,

    # Details
    url="https://bitbucket.org/hexacorp-ltd/orfium_oauth_provider",

    #
    license="LICENSE",
    description="A django-allauth provider for the Orfium.com music platform.",

    # Dependent packages (distributions)
    install_requires=[
        "django",
        "requests",
        "django-allauth",
    ],
)

from distutils.core import setup

setup(
    # Application name
    name="orfium_earnings_dashboard_sdk",

    # Version number
    version="0.2.0",

    # Application author details
    author="Dimitris Papaspyros",
    author_email="dimitris@orfium.com",

    # Packages
    packages=["orfium_earnings_dashboard_sdk"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://pypi.python.org/pypi/OrfiumEarningsDashboardSDK_010/",
    license="LICENSE",
    description="An SDK around the Orfium Earnings Dashboard API.",

    # Dependent packages (distributions)
    install_requires=[
        "requests",
    ],
)

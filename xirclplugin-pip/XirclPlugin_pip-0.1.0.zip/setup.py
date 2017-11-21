from distutils.core import setup

setup(
    # Application name:
    name="XirclPlugin_pip",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Shrawan Shinde",
    author_email="shrawan@nucleusads.com",

    # Packages
    packages=["xircl"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://pypi.python.org/pypi/XirclPlugin_pip/",

    #
    # license="LICENSE.txt",
    description="XIRCLS ​is​ ​a​ ​cross-marketing​ ​cloud​ ​software​ ​that​ ​enables​ ​online​ ​&​ ​offline​ ​merchants​ ​to partner​ ​together​ ​and​ ​directly​ ​market​ ​to​ ​each​ ​others'​ ​customers​ ​at​ ​the​ ​point​ ​of​ ​purchase. ",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "flask",
    ],
)
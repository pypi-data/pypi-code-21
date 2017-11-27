
from setuptools import setup, find_packages

NAME = "adys"

setup(name=NAME,
    version='0.1.1',
    author = "Loïc Paulevé",
    author_email = "loic.pauleve@lri.fr",
    description = "Simple python library for Boolean networks",
    long_description = "For teaching purpose",
    install_requires = [
        "pydotplus"
    ],
    license="CeCILL",
    packages = ["adys"],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    keywords="boolean networks, model checing, teaching",
)


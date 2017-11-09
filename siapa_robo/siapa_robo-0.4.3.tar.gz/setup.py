from setuptools import setup, find_packages

from siapa_robo.__init__ import __version__

setup(
    name="siapa_robo",
    version=__version__,
    author="Rafael Alves Ribeiro",
    author_email="rafael.alves.ribeiro@gmail.com",
    packages=["siapa_robo"],
    install_requires=[
        "brazilnum >= 0.8.8",
        "colorama >= 0.3.9",
        "lxml >= 3.7.3",
        "pandas >= 0.19.2",
        "selenium >= 3.3.1",
    ],
)

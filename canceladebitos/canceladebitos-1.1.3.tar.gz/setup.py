from setuptools import setup
from canceladebitos.__init__ import __version__

setup(
    name="canceladebitos",
    packages=["canceladebitos"],
    entry_points={
        "console_scripts": ['canceladebitos = canceladebitos.__main__:main']
        },
    version=__version__,
    description="Cancelamentos dos débitos renegociados em operações de parcelamento.",
    author="Rafael Alves Ribeiro",
    author_email="rafael.alves.ribeiro@gmail.com",
    install_requires=[
        "codecov",
        "fire",
        "numpy",
        "pandas",
        "psycopg2",
        "pytest",
        "selenium",
        "siapatools",
        "siapa_robo",
        "tqdm",        
    ],
    )

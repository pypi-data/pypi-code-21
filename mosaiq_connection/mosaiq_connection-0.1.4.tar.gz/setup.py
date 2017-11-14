from setuptools import setup

setup(
    name="mosaiq_connection",
    version="0.1.4",
    author="Simon Biggs",
    author_email="mail@simonbiggs.net",
    description="A toolbox for interacting with Mosaiq SQL.",
    packages=[
        "mosaiq_connection"
    ],
    license='AGPL3+',
    install_requires=[
        'numpy',
        'pandas',
        'pymssql',
        'keyring',
        'IPython'
    ]
)
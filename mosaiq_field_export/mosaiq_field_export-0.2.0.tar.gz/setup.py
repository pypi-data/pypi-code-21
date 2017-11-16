from setuptools import setup

setup(
    name="mosaiq_field_export",
    version="0.2.0",
    author="Simon Biggs",
    author_email="mail@simonbiggs.net",
    description="A toolbox for extracting field data from Mosaiq SQL.",
    packages=[
        "mosaiq_field_export"
    ],
    license='AGPL3+',
    install_requires=[
        'numpy',
        'pandas',
        'mosaiq_connection'
    ]
)
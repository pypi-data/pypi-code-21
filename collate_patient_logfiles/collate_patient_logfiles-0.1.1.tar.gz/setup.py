from setuptools import setup

setup(
    name="collate_patient_logfiles",
    version="0.1.1",
    author="Simon Biggs",
    author_email="mail@simonbiggs.net",
    description="Collate logfile data.",
    packages=[
        "collate_patient_logfiles"
    ],
    install_requires=[
        'attrs',
        'pyyaml',
        'numpy',
        'pandas'
    ],
    license='AGPL3+'
)
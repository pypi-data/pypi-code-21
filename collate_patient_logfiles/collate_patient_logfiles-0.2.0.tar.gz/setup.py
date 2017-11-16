from setuptools import setup

setup(
    name="collate_patient_logfiles",
    version="0.2.0",
    author="Simon Biggs",
    author_email="mail@simonbiggs.net",
    description="Collate logfile data.",
    packages=[
        "collate_patient_logfiles"
    ],
    entry_points={
        'console_scripts': [
            'collate_patient_logfiles=collate_patient_logfiles:main',
        ],
    },
    install_requires=[
        'attrs',
        'pyyaml',
        'numpy',
        'pandas'
    ],
    license='AGPL3+'
)
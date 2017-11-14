from setuptools import setup

setup(
    name="logfilenamer",
    version="0.4.1",
    author="Simon Biggs",
    author_email="mail@simonbiggs.net",
    description="Name log files using Mosaiq exports.",
    packages=[
        "logfilenamer"
    ],
    license='AGPL3+',
    entry_points={
        'console_scripts': [
            'logfilenamer=logfilenamer:main',
        ],
    },
    install_requires=[
        'trf2csv>=0.1.4',
        'mosaiq_connection>=0.1.2',
        'centre_config',
        'attrs',
        'pyyaml',
        'python-dateutil'
    ]
)
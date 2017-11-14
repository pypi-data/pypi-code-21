from setuptools import setup

setup(
    name="electron_insert_factors",
    version="1.0.0",
    author="Simon Biggs",
    author_email="mail@simonbiggs.net",
    description="Model electron insert factors.",
    packages=[
        "electron_insert_factors"
    ],
    # entry_points={
    #     'console_scripts': [
    #         'electron_insert_factors=electron_insert_factors:main',
    #     ],
    # },
    license='AGPL3+',
    install_requires=[
        'shapely',
        'numpy',
        'scipy'
    ],
    include_package_data=True
)
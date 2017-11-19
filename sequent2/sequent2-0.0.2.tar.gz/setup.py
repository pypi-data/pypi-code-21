from setuptools import setup

setup(
    name='sequent2',
    version='0.0.2',
    packages=['sequent2'],
    package_data={'sequent2': ['*.jo']},
    python_requires='>=3',
    install_requires=[
        'jojo',
    ]
)

from setuptools import setup

setup(
    name='jopylib',
    version='0.0.1',
    packages=['jopylib'],
    package_data={'jopylib': ['*.jo']},
    python_requires='>=3',
    install_requires=[
        'jojo',
    ]
)

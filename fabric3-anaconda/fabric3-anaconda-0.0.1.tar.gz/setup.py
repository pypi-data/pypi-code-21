from setuptools import setup, find_packages

setup(
    name="fabric3-anaconda",
    version="0.0.1",
    author='Barnaby Gray',
    author_email='barnaby@pickle.me.uk',
    url='http://pypi.python.org/pypi/fabric3-anaconda/',
    description=(
        "Some additional functions for working with anaconda environments "
        "in Fabric3."
    ),
    long_description=open('README.rst').read(),
    packages=find_packages(),
    install_requires=[
        'Fabric3'
    ]
)
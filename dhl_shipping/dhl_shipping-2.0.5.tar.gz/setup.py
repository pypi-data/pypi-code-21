#from distutils.core import setup
from setuptools import setup

setup(
    name='dhl_shipping',
    version='2.0.5',
    author='Hasanuzzaman Syed',
    author_email='hasanuzzaman.syed@gmail.com',
    packages=['dhl_shipping'],
    url='http://pypi.python.org/pypi/dhl_shipping/',
    license='LICENSE.txt',
    description='DHL Shipping - Quote, Pick Up, Shipping, Label Creation, Tracking',
    long_description=open('README.txt').read(),
    install_requires=[
        'xmltodict',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)

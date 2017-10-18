from distutils.core import setup
from setuptools import find_packages

setup(
    name='mintlabs',
    version='0.2.583',
    url='http://www.mint-labs.com',
    license='MIT',
    author='Mint Labs',
    author_email='tim@mint-labs.com',
    description='This is a Python API to interact with the ' +
                'Mint-Labs platform.',
    classifiers=['Development Status :: 3 - Alpha',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3.4'
                 ],
    packages=find_packages(exclude=['docs', 'test*']),
    install_requires=['requests==2.10.0']
)

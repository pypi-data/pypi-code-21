from setuptools import setup

setup(
    name="tinyjenkins",
    version="0.0.1",
    author="Josh Harlow",
    author_email="harlowja@gmail.com",
    description="A tiny jenkins client library",
    license="ASL",
    keywords="jenkins",
    packages=['tinyjenkins'],
    long_description=open("README").read(),
    install_requires=['requests', 'munch', 'oslo_utils'],
)

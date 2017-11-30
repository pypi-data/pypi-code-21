import os
from setuptools import setup

setup_pth = os.path.dirname(__file__)
readme_pth = os.path.join(setup_pth, 'README.md')
reqs_pth = os.path.join(setup_pth, 'requirements.txt')

setup(
    name='microacme',
    version="3.2.0",
    url="https://gitlab.mirus.io/domains/roadrunner/microacme/",
    author="Don Spaulding II",
    author_email="don@mirusresearch.com",
    long_description=open(readme_pth).read(),
    py_modules=["microacme"],
    zip_safe=True,
    install_requires=filter(bool, open(reqs_pth).read().splitlines())
)

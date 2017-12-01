import os
from setuptools import setup

setup_pth = os.path.dirname(__file__)
readme_pth = os.path.join(setup_pth, 'README.md')
reqs_pth = os.path.join(setup_pth, 'requirements.txt')
reqs = list(filter(bool, open(reqs_pth).read().splitlines()))

setup(
    name='microacme',
    version="3.2.4",
    url="https://gitlab.mirus.io/domains/roadrunner/microacme/",
    author="Don Spaulding II",
    author_email="don@mirusresearch.com",
    long_description=open(readme_pth).read(),
    py_modules=["microacme"],
    zip_safe=True,
    install_requires=reqs,
)

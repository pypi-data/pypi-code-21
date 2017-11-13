
from setuptools import setup, find_packages

NAME = "pypi-task-demo"
VERSION = "0.0.0"

REQUIRES = ["msrest>=0.2.0", 'mock']

setup(
    name=NAME,
    version=VERSION,
    description="PyPI demo",
    author="Vinod Kumar",    
    author_email="kuvinod@microsoft.com",
    url="https://github.com/kuvinodms/vsts-pypi-demo",
    keywords=["Microsoft", "VSTS", "Team Services", "SDK", "AzureTfs"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    """
)


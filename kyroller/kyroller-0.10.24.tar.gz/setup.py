from setuptools import setup, find_packages


PACKAGE = "kyroller"
VERSION = __import__(PACKAGE).__version__

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
required = [
    'termcolor==1.1.0',
    'click==6.7',
    'socketIO-client',
    'requests',
    'argparse'
]

setup(
    name="kyroller",
    version=VERSION,
    install_requires=required,
    author="ShangHai Shilai",
    author_email="developers@kuaiyutech.com",
    description='''快雨量化框架''',
    license="LGPL",
    keywords="stock kuaiyutech",
    url="http://packages.python.org/kyroller",
    packages=find_packages(exclude=["tests.*", "tests"]),
    long_description='''
        快雨量化框架，文档地址：https://doc.kuaiyutech.com
    ''',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    entry_points="""
    [console_scripts]
    kyroller_rollback=kyroller.bin.rollback:run
    """
)

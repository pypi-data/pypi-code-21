import codecs
import os
import sys

try:
    from setuptools import setup
except:
    from distutils.core import setup


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


NAME = "hello_rule_set"
PACKAGES = ["hello_rule_set", ]
DESCRIPTION = "This is a toolkit that outputs strong rules for the decision engine."
LONG_DESCRIPTION = read("README.txt")
KEYWORDS = "rule python package"
CONTRIBUTORS = """yan.wang"""

EMAIL = "644675188@qq.com"
URL = "https://gitlab.fraudmetrix.cn/yan.wang/ga_weight_optimization"
VERSION = "1.5.1"
LICENSE = "MIT"


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords=KEYWORDS,
    author=CONTRIBUTORS,
    author_email=EMAIL,
    url=URL,
    license=LICENSE,
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=True,
)

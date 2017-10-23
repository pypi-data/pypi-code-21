import codecs
import os
import sys
try:
  from setuptools import setup
except:
  from distutils.core import setup


def read(fname):
  return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


NAME = "zmop"
PACKAGES = ["zmop", "zmop/request"]
DESCRIPTION = "芝麻信用sdk"
LONG_DESCRIPTION = ""
KEYWORDS = ""
AUTHOR = "your_name"
AUTHOR_EMAIL = "youremail@email.com"
URL = "https://b.zmxy.com.cn/technology/sdkDownload.htm"
VERSION = "1.0.5"
LICENSE = "MIT"
CLASSFIERS = ['License :: OSI Approved :: MIT License','Programming Language :: Python','Intended Audience :: Developers','Operating System :: OS Independent']
setup(
  name=NAME,
  version=VERSION,
  description=DESCRIPTION,
  install_requires=["M2Crypto"],
  long_description=LONG_DESCRIPTION,
  classifiers=CLASSFIERS,
  keywords=KEYWORDS,
  author=AUTHOR,
  author_email=AUTHOR_EMAIL,
  url=URL,
  license=LICENSE,
  packages=PACKAGES,
  include_package_data=True,
  zip_safe=True,
)

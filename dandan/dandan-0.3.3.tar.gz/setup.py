from __future__ import absolute_import
import os
import sys
from setuptools import setup

NAME = "dandan"
INSTALL_REQUIRES = [
    "six",
    "requests",
    "beautifulsoup4",
]

base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)
try:
    import dandan
    version = dandan.__version__
except Exception:
    print("import project error")
    exit(0)

readme = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README")

setup(
    name=NAME,
    version=dandan.__version__,
    description="Several convenient tools for python programming",
    long_description=open(readme).read(),
    packages=[NAME],
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    author="ccyg",
    author_email="kjp1314@163.com",
    url="https://github.com/ccyg/dandan",
    license="MIT",
    include_package_data=True,
    zip_safe=True,
    platforms="any",
)


# python setup.py sdist bdist_wheel --universal
# twine upload dist/*

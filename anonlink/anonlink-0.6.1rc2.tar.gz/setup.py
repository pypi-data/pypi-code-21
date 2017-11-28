from setuptools import setup, find_packages
import os
here = os.path.abspath(os.path.dirname(__file__))


requirements = [
        "bitarray==0.8.1",
        "networkx==1.11",
        "cffi>=1.4.1",
    ]

setup(
    name="anonlink",
    version='0.6.1-rc.2',
    description='Anonymous linkage using cryptographic hashes and bloom filters',
long_description=open(os.path.join(here, "README.rst")).read(),
    url='https://github.com/n1analytics/anonlink',
    license='Apache',
    setup_requires=requirements,
    install_requires=requirements,
    test_requires=requirements,
    packages=find_packages(exclude=['tests']),
    package_data={'anonlink': ['data/*.csv']},
    # for cffi
    cffi_modules=["cpp_code/build_matcher.py:ffibuilder"],
    zip_safe=False,
    ext_package="anonlink"
)

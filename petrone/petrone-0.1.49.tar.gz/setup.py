from setuptools import setup, find_packages

setup(
    name = "petrone",
    version = "0.1.49",
    description = "Library for BYROBOT PETRONE",
    author = "BYROBOT",
    author_email = "dev@byrobot.co.kr",
    url = "http://www.byrobot.co.kr",
    packages = find_packages(),
    include_package_data = True,
    install_requires = ['pyserial', 'numpy', 'colorama'],
    long_description = open('README.md').read(),
)

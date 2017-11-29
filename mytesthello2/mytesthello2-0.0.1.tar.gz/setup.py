# -*- encoding: UTF-8 -*-
from setuptools import setup, find_packages
import io

VERSION = '0.0.1'

with io.open("README.md", encoding='utf-8') as f:
    long_description = f.read()

install_requires = open("requirements.txt").readlines()

setup(
    name="mytesthello2",  # pip 安装时用的名字
    version=VERSION,  # 当前版本，每次更新上传到pypi都需要修改
    author="prownd",
    author_email="prownd12345@gmail.com",
    url="https://mytesthello1.com/",
    keyworads="mytesthello1",
    description="this  is a hello test py file",
    long_description=long_description,
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    license='MIT License',
    classifiers=[],
    install_requires=install_requires,
)

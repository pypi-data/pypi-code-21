from __future__ import print_function
try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup


setup(
    name='central_lock',
    version='1.0.2',
    py_modules='central_lock',
    author='fanglei.zhao',
    author_email='281146581@qq.com',
    url='https://github.com/zhaofl2015/central_lock',
    description='A central lock for distribute applications',
    license='MIT',
    packages=['central_lock'],
    install_requires=['redis']
)
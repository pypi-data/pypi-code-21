# coding=utf-8
from setuptools import setup, find_packages
setup(
    name='huTrend',
    version=1.0,
    description=(
        '这仅是自己使用的整合包'
    ),
    author='trend',
    author_email='huyazhou_hadoop@163.com',
    maintainer='trend',
    maintainer_email='huyazhou_hadoop@163.com',
    license='BSD License',
    url="https://pypi.python.org/pypi",
    packages=find_packages(),
    platforms=["all"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
)
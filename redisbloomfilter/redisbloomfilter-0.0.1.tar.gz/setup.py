# coding=utf-8

from setuptools import setup, find_packages
import redisbloomfilter

myname = redisbloomfilter.__author__
myemail = '124303687@qq.com'

setup(
    name=redisbloomfilter.__name__,
    version=redisbloomfilter.__version__,
    description=redisbloomfilter.__doc__,
    long_description='bloomfilter base on redis for python',
    author=myname,
    author_email=myemail,
    maintainer=myname,
    maintainer_email=myemail,
    license='MIT',
    packages=find_packages(),
    install_requires=['redis>=2.10.5'],
    platforms=["all"],
    url='https://github.com/jeffreyzzh/redisbloomfilter',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
    ],
)

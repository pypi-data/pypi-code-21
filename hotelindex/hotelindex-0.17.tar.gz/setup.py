# coding=utf-8
from setuptools import setup, find_packages
setup(
      name='hotelindex',
      version='0.17',
      description="a crawler to get common hotel's room prices",
      keywords='crawler hotel plateno wyn88 ',
      author='zhoumx',
      author_email='franky.z.super@hotmail.com',
      url='https://github.com/hotelindex/hotelindex',
      classifiers={
        'Programming Language :: Python :: 3.6'
      },
      packages=['hotelindex','hotelindex.crawler'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[]
)
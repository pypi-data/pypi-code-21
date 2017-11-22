# coding=utf-8
from setuptools import setup, find_packages
setup(
      name='hotelindex',
      version='0.12',
      description="a crawler to get common hotel's room prices",
      keywords='crawler hotel plateno wyn88 ',
      author='zhoumx',
      author_email='franky.z.super@hotmail.com',
      url='https://github.com/zhoumx1987/hotelindex',
      classifiers={
        'Programming Language :: Python :: 3.6'
      },
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[]
)
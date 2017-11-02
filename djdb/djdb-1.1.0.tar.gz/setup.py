from setuptools import setup

setup(
    name='djdb',
    version='1.1.0',
    packages=['pydb','pydb.demo_db','pydb.model','pydb.settings',],
    description='a python databases api',
    url='https://github.com/HuangHongkai/pydb',
    install_requires=["Django >= 1.1.1",],
    author='dfsss',
    author_email='2523272490@qq.com',
)

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='asukiaaa_py_i2c_lcd',
    version='0.1.3',
    description='An i2c library to control AQM1602',
    long_description=long_description,
    url='https://github.com/asukiaaa/asukiaaa_py_i2c_lcd',
    author='Asuki Kono',
    author_email='asukiaaa@gmail.com',
    license='MIT',
    keywords='i2c lcd aqm1602 raspberry',
    packages=[
        'asukiaaa_py_i2c_lcd',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        # 'Programming Language :: Python :: 3.6',
    ],
)

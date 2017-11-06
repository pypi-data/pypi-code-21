## Developed By Sneurlax
## https://github.com/sneurlax



from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
  long_description = f.read()

setup(
  name='python-tuxexchange-Wrapper',
  version='1.0',
  description='Tux Exchange API wrapper for Python 2.7',
  long_description=long_description,
  url='https://github.com/olliecad1/python-tuxexchange-Wrapper',
  author='Oliver Morris',
  author_email='officialgamermorris@gmail.com',
  license='MIT',
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
  ],
  keywords='cryptocurrency exchange bitcoin trading Tuxexchange',
  packages=find_packages(exclude=['contrib', 'docs', 'tests', 'test', 'dist']),
  # install_requires=['peppercorn'],
  # extras_require={
  #   'dev': ['check-manifest'],
  #   'test': ['coverage'],
  # },
  # package_data={
  #   'sample': ['package_data.dat'],
  # },
  # data_files=[('my_data', ['data/data_file'])],
  # entry_points={
  #   'console_scripts': [
  #     'sample=sample:main',
  #   ],
  # },
)

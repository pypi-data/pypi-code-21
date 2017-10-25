# coding=utf-8
from distutils.core import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='pydeepl',
    packages=['pydeepl'],
    version='0.9',
    description='A python API wrapper for DeepL translating service.',
    long_description=readme(),
    author='Emilio Carrión Peñalba, frinkelpi',
    author_email='emiliok1997@gmail.com',
    url='https://github.com/EmilioK97/pydeepl',
    keywords=['deepl', 'API', 'translate', 'translation'],
    classifiers=[
      'Development Status :: 5 - Production/Stable',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
      'requests>=2.18.4',
    ],
)

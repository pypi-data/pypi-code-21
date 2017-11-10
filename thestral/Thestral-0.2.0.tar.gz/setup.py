# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Thestral',
    version='0.2.0',
    description='A simple single cell RNA-seq analysis package',
    long_description=long_description,
    url='https://github.com/Fang-Kevin/Thestral',
    author='Fang Jingwen',
    author_email='fjingwen@mail.ustc.edu.cn',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='Singel-cell RNA-seq',
    packages=find_packages(),
    install_requires=['numpy','pandas','matplotlib','seaborn','scipy','sklearn','fbpca','annoy'],
    python_requires='>=2.6, !=3.*.*,<4',
)

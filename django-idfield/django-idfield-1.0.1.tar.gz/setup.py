from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-idfield',
    version='1.0.1',
    author='Alex Lis',
    author_email='a@lis.space',
    description='Char ID filed Django',
    # keywords='sample setuptools development',
    long_description=long_description,
    license='MIT',
    url='https://github.com/lis-space/django-idfield',
    zip_safe=False,
    install_requires=[
        'django',
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3',
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        "Framework :: Django",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
    ],
)

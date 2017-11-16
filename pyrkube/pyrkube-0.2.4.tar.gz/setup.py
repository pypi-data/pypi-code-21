import re
from setuptools import setup, find_packages


with open('pyrkube/__init__.py', 'rt') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open('README.rst') as fd:
    long_description = fd.read()


setup(
    name='pyrkube',
    version=version,
    description='Readonly wrapper for pykube with a different focus',
    long_description=long_description,
    keywords=['kubernetes', 'clustering', 'templating'],
    author='Joe Black',
    author_email='me@joeblack.nyc',
    url='https://github.com/telephoneorg/pyrkube',
    download_url=(
        'https://github.com/telephoneorg/pyrkube/tarball/%s' % version),
    license='Apache 2.0',
    zip_safe=False,
    packages=find_packages(),
    package_data={'': ['LICENSE']},
    install_requires=[
        'pykube',
        'six'
    ],
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        "License :: OSI Approved :: Apache Software License",
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: System :: Clustering',
    ]
)

import re
from setuptools import setup, find_packages


with open('kzconfig/__init__.py', 'rt') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open('README.md') as fd:
    long_description = fd.read()


setup(
    name='kzconfig',
    version=version,
    description="Convenience library for configuring Kazoo & it's components",
    long_description=long_description,
    author='Joe Black',
    author_email='me@joeblack.nyc',
    url='https://github.com/telephoneorg/kzconfig',
    download_url=(
        'https://github.com/telephoneorg/kzconfig/tarball/v%s' % version),
    license='Apache 2.0',
    zip_safe=False,
    packages=find_packages(),
    package_data={'': ['LICENSE']},
    install_requires=[
        'requests',
        'click',
        'couchdb',
        'pyrkube>=0.2.5',
        'kazoo-sdk>=0.2.4',
        'dnsimple',
        'dnspython'
    ],
    entry_points=dict(
        console_scripts=[
            'sup = kzconfig.cli.sup:main',
            'install-kubectl = kzconfig.cli.kubectl:main'
        ]
    ),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Topic :: System',
        'Topic :: System :: Systems Administration'
    ]
)

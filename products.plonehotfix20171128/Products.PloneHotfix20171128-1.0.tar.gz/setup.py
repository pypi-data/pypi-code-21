from setuptools import setup, find_packages

import os

long_description = open(
    os.path.join('Products', 'PloneHotfix20171128', "README.txt")).read() + \
    "\n" + \
    open("CHANGES.rst").read()

version = '1.0'

setup(
    name='Products.PloneHotfix20171128',
    version=version,
    description="Various Plone hotfixes, 2017-11-28",
    long_description=long_description,
    # Get more strings from
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='plone security hotfix patch',
    author='Plone Security Team',
    author_email='security@plone.org',
    url='https://github.com/plone',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
    extras_require={
        'test': [
            'Pillow',
            'Plone',
            'Products.PloneTestCase'
        ],
    },
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """
)

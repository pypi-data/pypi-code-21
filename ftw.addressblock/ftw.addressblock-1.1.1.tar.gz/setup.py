from setuptools import setup, find_packages
import os

version = '1.1.1'
maintainer = '4teamwork'

contact_require = [
    'plone.formwidget.recaptcha',
]

geo_require = [
    'collective.geo.bundle [dexterity]',
    'collective.geo.mapwidget',
    'ftw.geo',
]

tests_require = [
    'ftw.builder',
    'ftw.testing',
    'ftw.testbrowser',
    'ftw.subsite',
] + geo_require + contact_require

extras_require = {
    'tests': tests_require,
    'geo': geo_require,
    'contact': contact_require,
}

setup(
    name='ftw.addressblock',
    version=version,
    description='ftw.addressblock',
    long_description=open('README.rst').read() + '\n' + open(
        os.path.join('docs', 'HISTORY.txt')).read(),

    # Get more strings from
    # http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    keywords='ftw addressblock simplelayout',
    author='4teamwork AG',
    author_email='mailto:info@4teamwork.ch',
    maintainer=maintainer,
    url='https://github.com/4teamwork/ftw.addressblock',
    license='GPL2',

    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['ftw', ],
    include_package_data=True,
    zip_safe=False,

    install_requires=[
        'ftw.autofeature',
        'ftw.simplelayout[contenttypes] >= 1.7.0',
        'ftw.upgrade',
        'Plone',
        'plone.api',
        'plone.app.dexterity',
        'plone.dexterity',
        'setuptools',
        'z3c.schema',
    ],

    tests_require=tests_require,
    extras_require=extras_require,

    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)

from setuptools import setup, find_packages
import os

version = '2.0'

setup(
    name='collective.soupstrainer',
    version=version,
    description="Clean up HTML using BeautifulSoup and filter rules.",
    long_description=(
        open("README.rst").read() + "\n" +
        open(os.path.join("docs", "HISTORY.rst")).read()),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",  # noqa
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2 :: Only",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Filters",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Utilities",
    ],
    keywords='html beautifulsoup clean filter rules',
    author='Florian Schulze',
    author_email='florian.schulze@gmx.net',
    url='http://svn.plone.org/svn/collective/collective.soupstrainer',
    license='GPLv2+',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'setuptools',
      'beautifulsoup4',
    ],
    entry_points={
      'console_scripts': ['soupstrainer = collective.soupstrainer:main'],
    },
    test_suite="collective.soupstrainer",
)

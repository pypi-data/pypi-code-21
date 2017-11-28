"""Staxing setup.py."""

from setuptools import setup, find_packages
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session=False)

reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='Staxing',
    version='0.0.52',
    packages=find_packages(),
    scripts=[],
    # zip_safe=True,
    # eager_resources=[],
    install_requires=reqs,
    # dependency_links=[],
    # namespace_packages=[],
    include_package_data=True,
    # exclude_package_data=True,
    package_data={
        '': ['*.txt', '*.rst', '*.md'],
    },
    # entry_points={},
    # extras_require={},
    # setup_requires=[],
    # use_2to3=True,
    # convert_2to3_doctests=[],
    # use_2to3_fixers=[],
    author='OpenStax QA',
    author_email='greg@openstax.org',
    description='Stax test base',
    license='Creative Commons Attribution 4.0 International Public License',
    keywords='',
    url='https://github.com/openstax/staxing',
    long_description=open('README.md').read(),
    # test_suite=''
    # tests_require=[],
    # test_loader='',
)

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE.md') as f:
    license = f.read()

setup(
    name='sepa_netherlands',
    version='0.2.8',
    description='Python library which handles communication with Dutch banks for processing SEPA eMandates.',
    long_description=readme,
    license=license,
    author='Vereniging Campus Kabel',
    author_email='info@vck.utwente.nl',
    url='https://github.com/VerenigingCampusKabel/python-sepa-netherlands',
    packages=find_packages(exclude=('tests')),
    install_requires=['sepa', 'requests', 'signxml'],
    test_suite='nose.collector',
    tests_require=['nose'],
    package_data={
        'sepa_netherlands': ['*.xsd']
    }
)

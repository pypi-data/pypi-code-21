from setuptools import setup, find_packages

setup(name='feedfinder2.7',
        version='0.1',
        description='pip installable copy of original Mark Pilgrim/Aaron Swartz feedfinder script',
        url='https://github.com/rutherford/feedfinder',
        author='Matt Rutherford',
        author_email='rutherford@clientsideweb.net',
        license='Public Domain',
        packages=find_packages(),
        zip_safe=False)

from setuptools import setup, find_packages

setup(
    name='rimac-analytics',          # This is the name of your PyPI-package.
    version='0.1',                   # Update the version number for new releases
    #scripts=['utils', 'common'],     # The name of your scipt, and also the command you'll be using for calling it
    description='Rimac Analytics API',
    author='diegoches',
    author_email='ddce.2005@gmail.com',
    zip_safe=False,
    url='https://bitbucket.org/rimac-analytics/rimac-analytics-api',
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    python_requires='>=3'
)

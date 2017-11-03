from setuptools import setup, find_packages


setup(
    name='transactionpro',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.2',

    description='Generate csv files for TransactionPro 6.0',
    # The project's main homepage.
    url='https://github.com/wontonst/transactionpro-py',

    # Author details
    author='Roy Zheng',
    author_email='roycraft3@gmail.com',

    # Choose your license
    license='MIT',

    # What does your project relate to?
    keywords='transactionpro transaction pro csv import',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    extras_require={
        'test': ['pytest'],
    },
)

from setuptools import setup, find_packages

setup(
    name='awspricemanager',
    description='AWS Price Manager - Pulls pricing information from AWS Price List',

    version='0.0.14',

    # Author details
    author='Adamson dela Cruz',
    author_email='adamson.delacruz@gmail.com',
    url='https://bitbucket.org/tochininja/aws-price-api/overview',
    license='BSD 3-Clause License',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Utilities',


        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='aws awspricing',

    #packages=['awspricemanager'],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    # install_requires=[
    #     'boto3','colorama','botocore','future','futures'
    # ],
    # entry_points='''
    #     [console_scripts]
    #     awsiot=commands.awsiot:main
    # ''',
    # entry_points={
    #     'console_scripts': [
    #         'awsiot=commands.awsiot:main',
    #     ],
    # },
)

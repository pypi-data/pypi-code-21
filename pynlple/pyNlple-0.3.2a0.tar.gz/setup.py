from setuptools import setup, find_packages

setup(
    name='pyNlple',
    packages=find_packages(exclude=['scripts', 'pynlple.youscan']),
    include_package_data=True,
    version='0.3.2a',
    description='NLP procedures in python brought to you by YouScan.',
    author='Paul Khudan',
    author_email='pk@youscan.io',
    company='YouScan Limited',
    url='https://github.com/YouScan/pyNlple',
    install_requires=['numpy',
                      'scikit-learn',
                      'requests>=2.9.1',
                      'pandas>=0.19.0',
                      'gensim>=2.1.0',
                      'elasticsearch>=2.0.0,<3.0.0',
                      'pymorphy2'],

    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='pynlple.tests',

)
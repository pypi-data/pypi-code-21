from setuptools import setup, find_packages

VERSION = '0.1'

long_description = open('README.rst', encoding='utf-8').read()

setup(
    name='laminated',
    version=VERSION,
    description='Dictionary like object with layers support',
    long_description=long_description,
    url='https://github.com/EvgeniyMakhmudov/laminated',
    author='Makhmudov Evgeniy',
    author_email='john_16@list.ru',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='dict dictionary layers',
    packages=find_packages(exclude=['laminated.benchs', 'laminated.tests']),
)

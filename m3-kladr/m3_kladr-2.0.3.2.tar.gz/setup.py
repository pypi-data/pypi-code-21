#coding: utf-8
from setuptools import setup, find_packages

REQUIREMENTS = [i.strip() for i in open("REQUIREMENTS").readlines()]

setup(
    name='m3_kladr',
    version='2.0.3.2',
    url='https://bitbucket.org/barsgroup/m3-kladr',
    license='MIT',
    author='BARS Group',
    description=u'Классификатор адресов Российской Федерации',
    author_email='bars@bars-open.ru',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=REQUIREMENTS,
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
    ],
)

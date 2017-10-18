
import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-paypal2',
    version='0.4.4',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=1.10',
        'django-extensions>=1.7.9',
        'django-model-utils==3.0.0',
        'paypalrestsdk==1.9.0',
    ],
    license='BSD License',
    description='paypal for django',
    long_description=README,
    author='Example',
    author_email='example@website.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-slxauth',
    version='1.5.0',
    packages=find_packages('.'),
    include_package_data=True,
    license='BSD License',
    description='Authentication provider for Solarlux Auth Service.',
    long_description=README,
    url='https://git.solarlux.com/sl-it-dev/slx8124_django-slxauth/',
    author='Enno Lohmeier',
    author_email='e.lohmeier@solarlux.de',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
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
    keywords='django auth account oauth',
    install_requires=['Django', 'cryptography', 'PyJWT', 'requests'],
)

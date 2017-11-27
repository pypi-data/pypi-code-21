import os
import site_exceptions_handler
from setuptools import find_packages, setup


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name=site_exceptions_handler.__name__,
    version=site_exceptions_handler.__version__,
    packages=find_packages(),
    url='https://bitbucket.org/Matthew-Stuart/user-agent-middleware',
    author=site_exceptions_handler.__author__,
    author_email=site_exceptions_handler.__author_email__,
    description=site_exceptions_handler.__description__,
    license='MIT',
    include_package_data=True,
    install_requires=[
        "jsonfield",
    ],
    platforms=['any'],
    zip_safe = False,
    classifiers=[
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: System :: Systems Administration',
    ],
)



with open(os.path.join(os.path.dirname(__file__), 'DELICENSE.txt')) as license_print:
    message = license_print.read()

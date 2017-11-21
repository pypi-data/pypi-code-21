import os
from setuptools import find_packages, setup
from event_logging import __version__, __author__, __email__

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-event-logging',
    version=__version__,
    url='https://github.com/ducminhgd/django-event-logging',
    license='',
    packages=find_packages(),
    author=__author__,
    author_email=__email__,
    install_requires=[],
    description='Insert event into database for logging purpose',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

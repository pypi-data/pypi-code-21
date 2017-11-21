import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-ohm2-handlers-light',
    version = '0.1.21',
    packages = ['ohm2_handlers_light'],
    install_requires = [
        'simplejson',
    ],
    include_package_data = True,
    license = 'BSD License',
    description = 'Django application to easily handle database requests and other tools',
    long_description = README,
    url = 'http://www.ohm2.cl/',
    author = 'Oliver Herrera',
    author_email = 'oliver@ohm2.cl',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

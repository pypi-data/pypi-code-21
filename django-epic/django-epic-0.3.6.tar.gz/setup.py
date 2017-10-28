import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-epic',
    version='0.3.6',
    packages=['epic'],
    install_requires=['django>=1.8.0',
                      'django-autocomplete-light>=3',
                      'django-bootstrap3-datetimepicker-2>=2.4.2',
                      'django-crispy-forms',
                      'openpyxl'],
    include_package_data=True,
    entry_points= {
        'console_scripts': [
            'kicad-to-epic-bom = epic.scripts.kicad_to_epic_bom:main'
        ]
    },
    license='MIT License',  # example license
    description='A Django app to manage electronic parts inventories '
    'for PCB manufacturing.',
    long_description=README,
    url='https://bitbucket.org/egauge/epic/',
    author='David Mosberger-Tang',
    author_email='davidm@egauge.net',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
    ],
)

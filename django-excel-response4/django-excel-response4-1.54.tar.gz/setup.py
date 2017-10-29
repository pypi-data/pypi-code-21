#!/usr/bin/env python
from distutils.core import setup

try:
	ld = open('README.rst').read()
except:
	ld = ''

version = '1.54'

setup(
    name='django-excel-response4',
    version=version,
    author='Chris Spencer',
    author_email='chrisspen@gmail.com',
    packages=['excel_response'],
    url='http://github.com/chrisspen/django-excel-response/',
    download_url='https://github.com/chrisspen/django-excel-response/tarball/%s' % version,
    description="""A subclass of HttpResponse which will transform a QuerySet,
or sequence of sequences, into either an Excel spreadsheet or
CSV file formatted for Excel, depending on the amount of data.
http://github.com/chrisspen/django-excel-response/
""",
    long_description=ld,
    requires=['xlwt'],
    keywords=['excel', 'django'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
    ],
)

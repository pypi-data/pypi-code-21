""" Periodic invoices for tryton
""" 

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
import ConfigParser, re

here = path.abspath(path.dirname(__file__))
MODULE = 'periodic_invoice'
PREFIX = 'mds'

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# tryton.cfg einlesen
config = ConfigParser.ConfigParser()
config.readfp(open('tryton.cfg'))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()

# Get module-versions
modversion = {}
with open(path.join(here, 'versiondep.txt'), encoding='utf-8') as f:
    l1 = f.readlines()
    for i in l1:
        l2 = i.strip().split(';')
        if len(l2) < 4:
            continue
        modversion[l2[0]] = {'min':l2[1], 'max':l2[2], 'prefix':l2[3]}

# tryton-version
major_version = 3
minor_version = 8

requires = ['python-dateutil']
for dep in info.get('depends', []):
    if not re.match(r'(ir|res|webdav)(\W|$)', dep):
        if dep in modversion.keys():
            prefix = 'mds'
            if len(modversion[dep]['prefix']) > 0:
                prefix = modversion[dep]['prefix']
                
            if len(modversion[dep]['max']) > 0:
                requires.append('%s_%s >= %s, <= %s' %
                    (prefix, dep, modversion[dep]['min'], modversion[dep]['max']))
            else :
                requires.append('%s_%s >= %s' %
                    (prefix, dep, modversion[dep]['min']))
        else :
          requires.append('%s_%s >= %s.%s, < %s.%s' %
                ('trytond', dep, major_version, minor_version,
                major_version, minor_version + 1))
requires.append('trytond >= %s.%s, < %s.%s' %
        (major_version, minor_version, major_version, minor_version + 1))

setup(name='%s_%s' % (PREFIX, MODULE),
    version=info.get('version', '0.0.1'),
    description='Tryton module to create periodic invoices',
    long_description=long_description,
    url='https://www.m-ds.de/',
    author='m-ds GmbH',
    author_email='service@m-ds.de',
    license='GPL-3',
    classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Environment :: Plugins',
    'Framework :: Tryton',
    'Intended Audience :: Developers',
    'Intended Audience :: Customer Service',
    'Intended Audience :: Information Technology',
    'Intended Audience :: Financial and Insurance Industry',
    'Topic :: Office/Business',
    'Topic :: Office/Business :: Financial :: Accounting',
    'Natural Language :: German',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Programming Language :: Python :: 2.7',
    ],

    keywords='tryton invoice periodic financial',
    package_dir={'trytond.modules.%s' % MODULE: '.'},
    packages=[
        'trytond.modules.%s' % MODULE,
        ],
    package_data={
        'trytond.modules.%s' % MODULE: (info.get('xml', [])
            + ['tryton.cfg', 'icon/*.svg', 'report/*.odt',
               'locale/*.po', 'view/*.xml', 'README.rst']),
        },

    install_requires=requires,
    zip_safe=False,
    entry_points=""" 
    [trytond.modules]
    %s = trytond.modules.%s
    """ % (MODULE, MODULE),
)

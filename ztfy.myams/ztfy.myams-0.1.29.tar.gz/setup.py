from setuptools import setup, find_packages
import os

DOCS = os.path.join(os.path.dirname(__file__),
                    'docs')

README = os.path.join(DOCS, 'README.txt')
HISTORY = os.path.join(DOCS, 'HISTORY.txt')
CONTRIBS = os.path.join(DOCS, 'CONTRIBUTORS.txt')

version = '0.1.29'
long_description = open(README).read() + '\n\n' + \
                   open(CONTRIBS).read() + '\n\n' + \
                   open(HISTORY).read()

tests_require = [
    'zope.testing',
]

setup(name='ztfy.myams',
      version=version,
      description="ZTFY new admin/application skin",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Thierry Florac',
      author_email='tflorac@ulthar.net',
      url='http://hg.ztfy.org/ztfy.myams',
      license='zpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['ztfy'],
      include_package_data=True,
      package_data={'': ['*.zcml', '*.txt', '*.pt', '*.pot', '*.po', '*.mo', '*.png', '*.gif', '*.jpeg', '*.jpg', '*.css', '*.js']},
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'fanstatic',
          'z3c.form',
          'z3c.formjs',
          'z3c.formui',
          'z3c.json',
          'z3c.jsonrpc',
          'z3c.language.negotiator',
          'z3c.language.session',
          'z3c.table',
          'z3c.template',
          'zope.annotation',
          'zope.authentication',
          'zope.component',
          'zope.container',
          'zope.event',
          'zope.exceptions',
          'zope.i18n',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.lifecycleevent',
          'zope.location',
          'zope.pagetemplate',
          'zope.publisher',
          'zope.schema',
          'zope.security',
          'zope.session',
          'zope.site',
          'zope.tales',
          'zope.traversing',
          'zope.viewlet',
          'ztfy.baseskin',
          'ztfy.extfile',
          'ztfy.file',
          'ztfy.mail',
          'ztfy.skin',
          'ztfy.utils',
      ],
      entry_points={
          'fanstatic.libraries': [
              'ztfy.myams = ztfy.myams:library'
          ]
      })

from setuptools import setup, find_packages
import os

DOCS = os.path.join(os.path.dirname(__file__),
                    'docs')

README = os.path.join(DOCS, 'README.txt')
HISTORY = os.path.join(DOCS, 'HISTORY.txt')
CONTRIBS = os.path.join(DOCS, 'CONTRIBUTORS.txt')

version = '0.1.20'
long_description = open(README).read() + '\n\n' + \
                   open(CONTRIBS).read() + '\n\n' + \
                   open(HISTORY).read()

tests_require = [
    'zope.testing',
]

setup(name='ztfy.sendit',
      version=version,
      description="ZTFY application used to share files",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: ZODB",
        "Framework :: Zope3",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Topic :: Communications :: File Sharing",
        "Topic :: Internet :: WWW/HTTP :: WSGI"
        ],
      keywords='ZTFY sendit application',
      author='Thierry Florac',
      author_email='tflorac@ulthar.net',
      url='http://hg.ztfy.org/ztfy.sendit',
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
          'hurry.query',
          'uuid',
          'z3c.form',
          'z3c.formjs',
          'z3c.jsonrpc',
          'z3c.language.negotiator',
          'z3c.language.switch',
          'z3c.table',
          'zc.catalog',
          'zope.annotation',
          'zope.app.content',
          'zope.app.file',
          'zope.app.publication',
          'zope.authentication',
          'zope.browserpage',
          'zope.catalog',
          'zope.component',
          'zope.componentvocabulary',
          'zope.container',
          'zope.dublincore',
          'zope.event',
          'zope.i18n',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.intid',
          'zope.lifecycleevent',
          'zope.location',
          'zope.pluggableauth',
          'zope.processlifetime',
          'zope.principalannotation',
          'zope.publisher',
          'zope.schema',
          'zope.security',
          'zope.sendmail',
          'zope.site',
          'zope.tales',
          'zope.traversing',
          'ztfy.appskin >= 0.2.0',
          'ztfy.captcha',
          'ztfy.extfile >= 0.2.13',
          'ztfy.file',
          'ztfy.i18n',
          'ztfy.jqueryui',
          'ztfy.mail',
          'ztfy.scheduler',
          'ztfy.security',
          'ztfy.skin >= 0.6.0',
          'ztfy.utils >= 0.4.4',
      ],
      entry_points={
          'fanstatic.libraries': [
              'ztfy.sendit = ztfy.sendit.skin:library'
          ]
      })

from distutils.core import setup

packages=[
    'horetu',
    'horetu.interfaces',
    'horetu.interfaces.wsgi',
    'funmap',
    'triedict',
]
extras_require={
  'django': ['Django>=1.9.12'],
  'wsgi': ['WebOb>=1.6.1'],
  'irc': ['irc>=15.0.6'],

  'docs': ['sphinxcontrib-autorun>=0.1'],
  'tests': ['BeautifulSoup4', 'pytest>=2.6.4', 'requests>=2.11.0'],
}
extras_require['all'] = extras_require['wsgi'] + \
                        extras_require['django'] + \
                        extras_require['irc']
extras_require['dev'] = extras_require['all'] + \
                        extras_require['docs'] + \
                        extras_require['tests']

setup(name='horetu',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='Make user interfaces to functions.',
      url='https://thomaslevine.com/scm/horetu/',
      packages=packages,
      install_requires=[
      ],
      extras_require=extras_require,
      tests_require=[
          'horetu[tests]',
      ],
      classifiers=[
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      version='0.4.1',
      license='AGPL',
      )

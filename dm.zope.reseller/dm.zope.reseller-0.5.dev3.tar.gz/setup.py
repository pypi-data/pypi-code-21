from os.path import abspath, dirname, join

try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      include_package_data=True,
      install_requires=[
        "dm.zope.schema>=2.1",
        "dm.reuse",
        "psycopg2",
        "decorator",
        "zope.rdb",
        "plone.z3cform",
        "Products.statusmessages",
        "python-gettext",
        "xlrd>=1.0",
        "xlwt>=1.2",
      ] ,
      namespace_packages=['dm', 'dm.zope'],
      zip_safe=False,
      #test_suite='dm.zope.reseller.tests.testsuite',
      #test_requires=[],
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'zope', 'reseller')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='dm.zope.reseller',
      version=pread('VERSION.txt').split('\n')[0],
      description="Zope package for reselling",
      long_description=pread('README.txt'),
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
#        'Development Status :: 3 - Alpha',
#        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Framework :: Zope2',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Home Automation',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Office/Business',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      url='http://pypi.python.org/pypi/dm.zope.reseller',
      packages=['dm', 'dm.zope', 'dm.zope.reseller'],
      keywords='product order delivery management reselling',
      license='BSD',
      **setupArgs
      )

from setuptools import setup, find_packages
import sys, os

def read(*pathnames):
    return open(os.path.join(os.path.dirname(__file__), *pathnames)).read()

version = '1.1.2'

setup(name='collective.portlet.carousel',
      version=version,
      description="Carousel for collective.panels",
      long_description='\n'.join([
          read('README.rst'),
          read('CHANGES.rst'),
      ]),
      classifiers=[],
      keywords='carousel panels',
      author='Bo Simonsen',
      author_email='bo@headnet.dk',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages = ['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.panels',
          'plone.app.portlets',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
)

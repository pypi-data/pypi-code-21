from setuptools import setup
setup(
  name='lp_unittest',
  packages=['lp_unittest'],
  package_data={'lp_unittest': ['migrations/*']},
  version='1.0.1',
  description='REST Unit Test Framework',
  author='Jim Simon',
  author_email='hello@launchpeer.com',
  url='https://github.com/Launchpeer/django-rest-unit-tests',
  download_url='https://github.com/Launchpeer/django-rest-unit-tests/archive/master.tar.gz',
  keywords=[],
  classifiers=[],
  install_requires=[
    'django-restframework',
    'django-rest-framework-social-oauth2',
    'oauth2_provider',
  ]
)

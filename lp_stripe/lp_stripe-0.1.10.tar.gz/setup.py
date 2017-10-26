from setuptools import setup
setup(
  name='lp_stripe',
  packages=['lp_stripe'],
  package_data={'lp_stripe': ['migrations/*', 'fixtures/*']},
  version='0.1.10',
  description='REST Framework Stripe Payments',
  author='Jim Simon',
  author_email='hello@launchpeer.com',
  url='https://github.com/Launchpeer/django-rest-stripe',
  download_url='https://github.com/Launchpeer/django-rest-stripe/archive/master.tar.gz',
  keywords=[],
  classifiers=[],
)
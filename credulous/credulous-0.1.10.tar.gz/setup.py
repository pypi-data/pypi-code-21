from setuptools import setup

from distutils.core import setup
setup(
  name='credulous',
  packages=['credulous'], # this must be the same as the name above
  version='0.1.10',
  description='Tool for generating API credentials. Google API is supported.',
  author='David O\'Connor',
  author_email='david.o@brainlabsdigital.com',
  url='https://github.com/davido-brainlabs/pycredulous', # use the URL to the github repo
  keywords=['oauth2', 'authentication', 'google', 'googleads-api-client-python'], # arbitrary keywords
  classifiers=[],
  install_requires=[
		'oauth2client',
    'future',
  ],
  entry_points={
    'console_scripts': [
      'credulous = credulous.credulous:main',
    ]
  }
)
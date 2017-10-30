from setuptools import setup,find_packages

setup(name='ppss_auth',
  version='0.2.9',
  description='simple auth scheme for pyramid',
  author='pdepmcp',
  author_email='d.cariboni@pingpongstars.it',
  url='http://www.pingpongstars.it',
  #packages=['src/test1'],
  packages=find_packages(),
  include_package_data=True,

)



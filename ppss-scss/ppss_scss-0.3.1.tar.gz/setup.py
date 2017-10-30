from setuptools import setup,find_packages

setup(name='ppss_scss',
      version='0.3.1',
      description='simple scsscompiler for pyramid',
      author='pdepmcp',
      author_email='d.cariboni@pingpongstars.it',
      url='http://www.pingpongstars.it',
      #packages=['src/test1'],
      install_requires=['sass','pyramid>=1.5.7'],
      packages=find_packages()
     )



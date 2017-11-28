from setuptools import setup, find_packages

setup(name='daon',
      version='0.1.4',
      install_requires=['py4j'],
      description='Daon Korean Analyzer',
      url='http://github.com/rasoio/daon-python',
      author='rasoio',
      author_email='rasoio@naver.com',
      license='MIT',
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      package_data={'daon':['java/daonCore.jar']},
      zip_safe=False)

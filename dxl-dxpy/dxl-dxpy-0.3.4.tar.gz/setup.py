from setuptools import setup, find_packages
setup(name='dxl-dxpy',
      version='0.3.4',
      description='Duplicate components library python sub-library.',
      url='https://github.com/Hong-Xiang/dxl',
      author='Hong Xiang',
      author_email='hx.hongxiang@gmail.com',
      license='MIT',
      packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "dxpy.tests"]),
      install_requires=[
          'rx',
          'flask_restful',
          'flask_sqlalchemy',
          'graphviz',
          'fs',
          'apscheduler'
      ],
      scripts=['bin/dxpy'],
      zip_safe=False)

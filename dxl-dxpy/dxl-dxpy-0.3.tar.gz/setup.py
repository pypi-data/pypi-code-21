from setuptools import setup

setup(name='dxl-dxpy',
      version='0.3',
      description='Duplicate components library python sub-library.',
      url='https://github.com/Hong-Xiang/dxl',
      author='Hong Xiang',
      author_email='hx.hongxiang@gmail.com',
      license='MIT',
      packages=['dxpy'],
      install_requires=[
          'rx',
          'flask_restful',
          'flask_sqlalchemy',
          'graphviz',
          'fs'
      ],
      scripts=['bin/dxpy'],
      zip_safe=False)

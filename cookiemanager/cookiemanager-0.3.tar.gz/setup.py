from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='cookiemanager',  #打包后的包文件名
      version='0.3',   #版本
      description='description',
      author='ider',
      author_email='ruangnazi@gmail.com',
      url='https://github.com/ider-zh/cookiemanager',
      long_description = read('README.md'),
      scripts = ['cookiemanager.py'],
)

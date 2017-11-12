#!/usr/bin/env python3
from setuptools import setup ,find_packages

import yxspkg_songzgif
install_modules=[]
for i in ['PyQt5','numpy','moviepy','imageio','scipy']:
	try:
		exec('import '+i)
	except:
		install_modules.append(i)
setup(name='yxspkg_songzgif',   
      version=yxspkg_songzgif.__version__,    
      description='A GUI to make gif based on pyqt5',    
      author='Blacksong',    
      install_requires=install_modules,
      author_email='blacksong@qq.com',
      long_description=open('README.rst', 'r').read(),       
      url='https://github.com/blacksong',
      packages=find_packages(), 
      classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
)   

 #!/usr/bin/env python3
 # -*- coding: utf-8 -*- 
from setuptools import setup, find_packages

setup(name='ibmBluegroup',
      version='1.04',
      description="IBM Bluegroup API",
      packages=find_packages(),
      keywords='Bluegroup',
      author='ThomasIBM',
      author_email='guojial@cn.ibm.com',
      license="Apache License, Version 2.0",
      url='https://github.com/ThomasIBM/ibmBluegroup',
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'httplib2',
      ],

)
 #!/usr/bin/env python3
 # -*- coding: utf-8 -*- 
from setuptools import setup, find_packages

setup(name='ibmBluepages',
      version='1.00',
      description="IBM Bluepages API",
      packages=find_packages(),
      keywords='Bluepages',
      author='ThomasIBM',
      author_email='guojial@cn.ibm.com',
      license="Apache License, Version 2.0",
      url='https://github.com/ThomasIBM/ibmBluepages',
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'httplib2',
      ],

)
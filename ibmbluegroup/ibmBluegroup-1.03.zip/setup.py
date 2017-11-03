 #!/usr/bin/env python3
 # -*- coding: utf-8 -*- 
from distutils.core import setup

setup(name='ibmBluegroup',
      version='1.03',
      description="IBM Bluegroup API",
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
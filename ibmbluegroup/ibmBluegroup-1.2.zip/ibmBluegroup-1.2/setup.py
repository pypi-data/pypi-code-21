 #!/usr/bin/env python3
 # -*- coding: utf-8 -*- 
from setuptools import setup

setup(name='ibmBluegroup',
      version='1.02',
      description="IBM Bluegroup API",
      keywords='Bluegroup',
      author='ThomasIBM',
      author_email='guojial@cn.ibm.com',
      url='https://github.com/ThomasIBM',
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'httplib2',
      ],
)
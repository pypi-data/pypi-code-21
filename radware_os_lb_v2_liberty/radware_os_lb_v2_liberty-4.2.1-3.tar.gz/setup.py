#!/usr/bin/env python
# Copyright (c) 2017 Radware LTD. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# THIS FILE IS MANAGED BY THE GLOBAL REQUIREMENTS REPO - DO NOT EDIT
import os
from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='radware_os_lb_v2_liberty',
      version='4.2.1-3',
      description='Radware LBaaS v2 driver for Openstack Liberty',
      long_description = readme(),
      classifiers=[
        'Environment :: OpenStack',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7'
      ],
      keywords=['openstack','radware','lbaasv2'],
      url='https://pypi.python.org/pypi/radware_os_lb_v2_liberty',
      author='Evgeny Fedoruk, Radware',
      author_email='evgenyf@radware.com',
      packages=['radware_os_lb_v2_liberty'],
      zip_safe=False)

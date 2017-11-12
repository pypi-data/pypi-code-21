# Copyright 2012-2014 Ravello Systems, Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys

if sys.version_info[:2] <= (2,6):
    from unittest2 import TestLoader, TextTestRunner
else:
    from unittest import TestLoader, TextTestRunner


testdir = os.path.split(os.path.abspath(__file__))[0]
topdir = os.path.split(testdir)[0]
libdir = os.path.join(topdir, 'lib')

os.chdir(testdir)
sys.path.insert(0, libdir)

loader = TestLoader()
tests = loader.discover('.', 'flow_*.py')

runner = TextTestRunner(verbosity=2, buffer=True)
runner.run(tests)

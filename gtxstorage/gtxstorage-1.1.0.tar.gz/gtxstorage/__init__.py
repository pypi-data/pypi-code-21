# -*- coding: utf-8 -*-
# GTXStorage Python Library for Amazon S3 Compatible Cloud Storage,
# (C) 2015, 2016, 2017 GTXStorage, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
gtxstorage - GTXStorage Python Library for Amazon S3 Compatible Cloud Storage
~~~~~~~~~~~~~~~~~~~~~

   >>> import gtxstorage
   >>> gtxstorage = GTXStorage('https://s3.amazonaws.com')
   >>> for bucket in gtxstorage.list_buckets():
   ...     print(bucket.name)

:copyright: (c) 2015, 2016, 2017 by GTXStorage, Inc.
:license: Apache 2.0, see LICENSE for more details.
"""

__title__ = 'gtxstorage-py'
__author__ = 'GTXStorage, Inc.'
__version__ = '1.1.0'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2015, 2016, 2017 GTXStorage, Inc.'

from .api import GTXStorage
from .error import ResponseError
from .post_policy import PostPolicy
from .copy_conditions import CopyConditions
from .definitions import Bucket, Object

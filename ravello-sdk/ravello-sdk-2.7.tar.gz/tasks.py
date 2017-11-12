#!/usr/bin/env python
#
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

from __future__ import absolute_import, print_function

from invoke import run, task


@task
def clean():
    run('find . -name __pycache__ | xargs rm -rf', echo=True)
    run('find . -name *.so | xargs rm -f', echo=True)
    run('rm -rf build dist', echo=True)


@task(clean)
def develop():
    run('python setup.py build', echo=True)
    if develop:
        run('python setup.py develop', echo=True)

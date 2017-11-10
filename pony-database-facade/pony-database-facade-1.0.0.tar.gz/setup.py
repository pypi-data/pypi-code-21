# coding: utf-8
#
# Copyright 2017 Kirill Vercetti
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

from setuptools import setup, find_packages


setup(
    name="pony-database-facade",
    version="1.0.0",
    author="Kirill Vercetti",
    author_email="office@kyzima-spb.com",
    license="Apache-2.0",
    url="https://github.com/kyzima-spb/pony-database-facade",
    description="PonyORM Database object Facade",
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "six",
        "pony"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python"
    ]
)

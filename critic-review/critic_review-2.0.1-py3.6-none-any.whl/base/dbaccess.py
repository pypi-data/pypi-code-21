# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2012 Jens Lindström, Opera Software ASA
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.

import base

try:
    configuration = base.configuration()
except base.MissingConfiguration:
    configuration = {}

if "database.driver" in configuration:
    if configuration["database.driver"] == "postgresql":
        import psycopg2 as driver

        TransactionRollbackError = driver.extensions.TransactionRollbackError
    else:
        import sqlitecompat as driver

        # SQLite doesn't appear to be throwing this type of error.
        class TransactionRollbackError(Exception):
            pass

    IntegrityError = driver.IntegrityError
    OperationalError = driver.OperationalError
    ProgrammingError = driver.ProgrammingError

    def connect():
        parameters = configuration["database.parameters"]
        return driver.connect(*parameters["args"], **parameters["kwargs"])
else:
    IntegrityError = base.Error
    OperationalError = base.Error
    ProgrammingError = base.Error
    TransactionRollbackError = base.Error

    def connect():
        raise base.MissingConfiguration

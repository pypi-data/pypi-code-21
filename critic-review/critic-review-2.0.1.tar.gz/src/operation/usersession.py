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

import api
import dbutils
import auth

from operation import Operation, OperationResult, OperationFailure, Request

class ValidateLogin(Operation):
    def __init__(self):
        Operation.__init__(self, { "req": Request,
                                   "fields": { str: str }},
                           accept_anonymous_user=True)

    def process(self, db, user, req, fields):
        if api.critic.settings().frontend.authentication_mode != "critic":
            raise OperationFailure(
                code="notsupported",
                title="Not supported",
                message="This operation is not supported on this system.")

        if not user.isAnonymous():
            return OperationResult()

        try:
            auth.Database.get().authenticate(db, fields)
        except auth.AuthenticationFailed as error:
            return OperationResult(message=str(error))
        except auth.WrongPassword:
            return OperationResult(message="Wrong password!")

        auth.createSessionId(db, req, db.user, db.authentication_labels)

        return OperationResult()

    def sanitize(self, value):
        sanitized = value.copy()
        for field in auth.Database.get().getFields():
            if field[0]:
                sanitized["fields"][field[1]] = "****"
        return sanitized

class EndSession(Operation):
    def __init__(self):
        Operation.__init__(self, { "req": Request })

    def process(self, db, user, req):
        if api.critic.settings().frontend.authentication_mode == "host":
            raise OperationFailure(
                code="notsupported",
                title="Not supported",
                message="This operation is not supported on this system.")

        if not auth.deleteSessionId(db, req, user):
            raise OperationFailure(
                code="notsignedout",
                title="Not signed out",
                message="You were not signed out.")

        if not api.critic.settings().users.allow_anonymous:
            return OperationResult(target_url="/")

        return OperationResult()

foo = 10

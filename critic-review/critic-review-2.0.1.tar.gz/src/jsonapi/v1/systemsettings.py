# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2017 the Critic contributors, Opera Software ASA
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
import jsonapi

@jsonapi.PrimaryResource
class SystemSettings(object):
    """The system settings."""

    name = "systemsettings"
    value_class = api.systemsetting.SystemSetting
    exceptions = (api.systemsetting.SystemSettingError,)

    @staticmethod
    def json(value, parameters):
        """SystemSetting {
             "id": string, // the setting's id (key)
             "value": any, // the setting's value
           }"""

        return parameters.filtered(
            "systemsettings", {
                "id": value.id,
                "value": value.value
            })

    @staticmethod
    def single(parameters, argument):
        """Retrieve one (or more) system settings.

           SETTING_ID : string

           Retrieve a system setting identified by its unique id."""

        return api.systemsetting.fetch(parameters.critic, argument)

    @staticmethod
    def multiple(parameters):
        """Retrieve all system settings.

           prefix : PREFIX : string

           Return only settings whose id has the specified prefix. Setting ids
           are always a sequence of full stop-separated identifiers (at least
           two, and thus at least one full stop.) The prefix should be the first
           such identifier, or a sequence of them separated by full stops. There
           should be no trailing flul stop in the prefix."""

        prefix_parameter = parameters.getQueryParameter("prefix")
        return api.systemsetting.fetchAll(
            parameters.critic, prefix=prefix_parameter)

    @staticmethod
    def update(parameters, value, values, data):
        if values and len(values) != 1:
            raise jsonapi.UsageError(
                "Updating multiple system settings not supported")

        critic = parameters.critic

        if values:
            value, = values

        converted = jsonapi.convert(
            parameters, {"value": jsonapi.check.TypeChecker()}, data)

        with api.transaction.Transaction(critic) as transaction:
            transaction.setSystemSetting(value, converted["value"])

        return value

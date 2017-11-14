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

import json

import api
import base

from . import apiobject

class SystemSetting(apiobject.APIObject):
    wrapper_class = api.systemsetting.SystemSetting

    def __init__(self, setting_id, value, is_privileged):
       self.id = setting_id
       self.value = json.loads(value)
       self.is_privileged = is_privileged

    def wrap(self, critic):
        if self.is_privileged:
            api.PermissionDenied.raiseUnlessSystem(critic)
        return super().wrap(critic)

    @staticmethod
    def refresh(critic, tables, cached_settings):
        if "systemsettings" not in tables:
            return

        SystemSetting.updateAll(
            critic,
            """SELECT key, value, privileged
                 FROM systemsettings
                WHERE key=ANY (%s)""",
            cached_settings)

@SystemSetting.cached(api.systemsetting.InvalidSystemSettingId)
def fetch(critic, setting_id):
    cursor = critic.getDatabaseCursor()
    cursor.execute(
        """SELECT key, value, privileged
             FROM systemsettings
            WHERE identity=%s
              AND key=%s""",
        (base.configuration()["system.identity"], setting_id))
    return SystemSetting.make(critic, cursor)

@SystemSetting.cachedMany(api.systemsetting.InvalidSystemSettingIds)
def fetchMany(critic, setting_ids):
    cursor = critic.getDatabaseCursor()
    cursor.execute(
        """SELECT key, value, privileged
             FROM systemsettings
            WHERE identity=%s
              AND key=ANY (%s)""",
        (base.configuration()["system.identity"], setting_ids))
    return SystemSetting.make(critic, cursor)

def fetchAll(critic, prefix):
    cursor = critic.getDatabaseCursor()
    try:
        api.PermissionDenied.raiseUnlessSystem(critic)
    except api.PermissionDenied:
        include_privileged = False
    else:
        include_privileged = True
    if prefix is None:
        cursor.execute(
            """SELECT key, value, privileged
                 FROM systemsettings
                WHERE identity=%s
                  AND (NOT privileged OR %s)""",
            (base.configuration()["system.identity"], include_privileged))
    else:
        if "%" in prefix:
            raise api.systemsetting.InvalidPrefix(prefix)
        cursor.execute(
            """SELECT key, value, privileged
                 FROM systemsettings
                WHERE identity=%s
                  AND key LIKE %s
                  AND (NOT privileged OR %s)""",
            (base.configuration()["system.identity"], prefix + ".%",
             include_privileged))
    return list(SystemSetting.make(critic, cursor))

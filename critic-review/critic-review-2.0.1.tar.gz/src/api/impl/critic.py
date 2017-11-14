# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2014 the Critic contributors, Opera Software ASA
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

import threading

import api
import dbutils

class NoKey(object):
    pass

settings = None
settings_lock = threading.Lock()

class Critic(object):
    def __init__(self, session_type):
        self.session_type = session_type
        self.database = None
        self.actual_user = None
        self.access_token = None
        self.__cache = {}

    def setDatabase(self, database):
        self.database = database

    def getEffectiveUser(self, critic):
        if self.actual_user:
            return self.actual_user
        return api.user.anonymous(critic)

    def getSettings(self, critic):
        global settings, settings_lock
        if settings is None:
            with settings_lock:
                if settings is None:
                    settings = Settings(api.systemsetting.fetchAll(critic))
        return settings

    def lookup(self, cls, key=NoKey):
        objects = self.__cache[cls]
        if key is NoKey:
            return objects
        return objects[key]

    def assign(self, cls, key, value):
        self.__cache.setdefault(cls, {})[key] = value

    def close(self):
        self.database.close()

    @staticmethod
    def transactionEnded(critic, tables):
        for Implementation, cached_objects in critic._impl.__cache.items():
            if hasattr(Implementation, "refresh"):
                Implementation.refresh(critic, tables, cached_objects)
        return True

class SettingsGroup():
    def __init__(self, prefix=""):
        self.__items = {}
        self.__prefix = prefix

    def __getattr__(self, key):
        try:
            return self.__items[key]
        except KeyError:
            raise AttributeError(key)

    def _add(self, setting):
        prefix, _, rest = setting.id[len(self.__prefix):].partition(".")
        existing = self.__items.get(prefix)
        if rest:
            if existing is None:
                existing = self.__items[prefix] = SettingsGroup(prefix + ".")
            else:
                assert isinstance(existing, SettingsGroup)
            existing._add(setting)
        else:
            assert existing is None
            self.__items[prefix] = setting.value

class Settings(SettingsGroup):
    def __init__(self, settings):
        super().__init__()
        for setting in settings:
            self._add(setting)

def startSession(for_user, for_system, for_testing):
    if for_user:
        session_type = "user"
    elif for_system:
        session_type = "system"
    else:
        session_type = "testing"

    critic = api.critic.Critic(Critic(session_type))
    critic._impl.setDatabase(dbutils.Database(critic))
    critic._impl.getSettings(critic)

    if for_system or for_testing:
        critic.database.setUser(dbutils.User.makeSystem(critic.database))

    return critic

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

class SystemSettingError(api.APIError):
    """Base exception for all errors related to the SystemSetting class"""
    pass

class InvalidSystemSettingIds(SystemSettingError):
    """Raised when one or more invalid system setting ids is used"""

    def __init__(self, values):
        """Constructor"""
        super().__init__("Invalid system settings: %r" % values)
        self.values = values

class InvalidSystemSettingId(SystemSettingError):
    """Raised when a single invalid system setting id is used"""

    def __init__(self, value):
        """Constructor"""
        super().__init__("Invalid system setting: %r" % value)
        self.value = value

class InvalidPrefix(SystemSettingError):
    """Raised when an invalid prefix is used"""

    def __init__(self, value):
        """Constructor"""
        super().__init__("Invalid system setting prefix: %r" % value)
        self.value = value

class SystemSetting(api.APIObject):
    @property
    def id(self):
        """The setting's unique id"""
        return self._impl.id

    @property
    def value(self):
        """The setting's value"""
        return self._impl.value

def fetch(critic, setting_id):
    """Fetch a SystemSetting object with the given id"""
    import api.impl
    assert isinstance(critic, api.critic.Critic)
    return api.impl.systemsetting.fetch(critic, str(setting_id))

def fetchMany(critic, setting_ids):
    """Fetch many SystemSetting object with the given ids"""
    import api.impl
    assert isinstance(critic, api.critic.Critic)
    setting_ids = [str(setting_id) for setting_id in setting_ids]
    return api.impl.systemsetting.fetchMany(critic, setting_ids)

def fetchAll(critic, *, prefix=None):
    """Fetch SystemSetting objects for all system settings

       If |prefix| is not None, fetch only settings whose id has the specified
       prefix."""
    import api.impl
    assert isinstance(critic, api.critic.Critic)
    if prefix is not None:
        prefix = str(prefix)
    return api.impl.systemsetting.fetchAll(critic, prefix)

def get(critic, setting_id=None, *, prefix=None):
    """Fetch a system setting's value"""
    assert (setting_id is None) != (prefix is None)
    if setting_id is None:
        return {
            setting.id: setting.value
            for setting in fetchAll(critic, prefix=prefix)
        }
    return fetch(critic, setting_id).value

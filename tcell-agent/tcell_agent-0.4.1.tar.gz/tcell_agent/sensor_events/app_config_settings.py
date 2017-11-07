# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from . import SensorEvent


class AppConfigSettings(SensorEvent):
    def __init__(self, package, section, name, value, prefix=None):
        super(AppConfigSettings, self).__init__("app_config_setting", ensure_delivery=True, queue_wait=True)
        self.setting(package, section, prefix, name, value)

    def setting(self, package, section, prefix, name, value):
        self["package"] = package
        self["section"] = section
        if prefix is not None:
            self["prefix"] = prefix
        self["name"] = name
        self["value"] = str(value)

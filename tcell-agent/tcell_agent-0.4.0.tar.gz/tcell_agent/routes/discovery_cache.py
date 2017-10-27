# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

""" Agent Module handles communication and instrumentation, this
is the main class.
"""
from __future__ import unicode_literals
from __future__ import print_function

import os

from ..config import CONFIGURATION


class DiscoveryCache:
    def current_cache_json(self, discovery_type):
        cache_filename = os.path.join(CONFIGURATION.tcell_folder, CONFIGURATION.cache_folder, "discovery_cache", ".",
                                      discovery_cache)
        if os.path.isfile(cache_filename) == True:
            cache_json = {}
        try:
            with open(cache_filename) as data_file:
                json_data = data_file.read()
                cache_json = json.loads(json_data)
        except Exception as e:
            LOGGER.error("Error loading configuration file {e}".format(e=e))
            LOGGER.debug(e, exc_info=True)
        return cache_json

    def update_cache(self, discovery_type, discovery_table_json):
        cache_filename = os.path.join(CONFIGURATION.tcell_folder, CONFIGURATION.cache_folder, "discovery_cache", ".",
                                      discovery_cache)
        try:
            with open(self.cache_filename, "w") as data_file:
                json.dump(discovery_table_json, data_file, indent=2)
            data_file.close()
        except Exception as e:
            LOGGER.error("Error writing configuration file {e}".format(e=e))
            LOGGER.debug(e, exc_info=True)
        return

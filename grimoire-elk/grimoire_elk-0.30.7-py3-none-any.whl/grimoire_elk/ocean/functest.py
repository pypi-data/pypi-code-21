#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# StackExchange Ocean feeder
#
# Copyright (C) 2015 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#   Alvaro del Castillo San Felix <acs@bitergia.com>
#

from .elastic import ElasticOcean

class FunctestOcean(ElasticOcean):
    """Functest Ocean feeder"""

    def _fix_item(self, item):
        if 'details' in item["data"]:
            if isinstance(item["data"]["details"], str):
                # Wrong format. This field is a dict with the details or
                # and array with dicts
                item["data"]["details"] = {}

    def get_elastic_mappings(self):
        # data.details has {} [] and "" values!
        mapping = '''
         {
            "dynamic":true,
                "properties": {
                    "data": {
                        "properties": {
                            "details": {
                                "dynamic":false,
                                "properties": {}
                            },
                            "trust_indicator": {
                                "dynamic":false,
                                "properties": {}
                            }
                        }
                    }
                }
        }
        '''

        return {"items":mapping}

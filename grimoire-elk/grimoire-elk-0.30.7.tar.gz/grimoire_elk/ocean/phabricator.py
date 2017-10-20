#!/usr/bin/python3
# -*- coding: utf-8 -*-
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

class PhabricatorOcean(ElasticOcean):
    """Phabricator Ocean feeder"""

    def _fix_item(self, item):
        item["ocean-unique-id"] = item["uuid"]
        # https://discuss.elastic.co/t/field-name-cannot-contain/33251/16
        if 'custom.external_reference' in item["data"]['fields']:
            item["data"]['fields']["custom_external_reference"] = item["data"]['fields'].pop("custom.external_reference")
        if 'custom.security_topic' in item["data"]['fields']:
            item["data"]['fields']["custom_security_topic"] = item["data"]['fields'].pop("custom.security_topic")

    def get_elastic_mappings(self):
        # This field data.transaction has string arrays and dicts arrays
        mapping = '''
         {
            "dynamic":true,
                "properties": {
                    "data": {
                        "properties": {
                            "transactions": {
                                "dynamic":false,
                                "properties": {}
                            }
                        }
                    }
                }
        }
        '''

        return {"items":mapping}

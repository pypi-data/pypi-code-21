
# -*- coding: utf-8 -*-
"""
Datary sdk Members File
"""
from urllib.parse import urljoin
from datary.auth import DataryAuth

import structlog

logger = structlog.getLogger(__name__)


class DataryMembers(DataryAuth):
    """
    Datary Members module class
    """

    def get_members(self, member_uuid='', member_name='', **kwargs):
        """
        ==============  =============   ====================================
        Parameter       Type            Description
        ==============  =============   ====================================
        member_uuid     str             member_uuid uuid
        member_name     str             member_name

        limit           int             number of results limit (default=20)
        ==============  =============   ====================================

        Returns:
            (list or dict) repository with the given member_uuid or member_name
        """

        logger.info("Getting Datary members")

        url = urljoin(
            self.URL_BASE,
            "search/members")

        params = {
            'limit': kwargs.get('limit', 20),
            'hint': kwargs.get('hint', None)
            }

        response = self.request(
            url, 'GET', **{'headers': self.headers, 'params': params})

        members_data = response.json() if response else {}
        member = {}

        if member_name or member_uuid:
            for member_data in members_data:

                member_data_uuid = member_data.get('uuid')
                member_data_username = member_data.get('username')

                if member_uuid and member_data_uuid == member_uuid:
                    member = member_data
                    break

                elif member_name and member_data_username == member_name:
                    member = member_data
                    break
        else:
            member = members_data

        return member

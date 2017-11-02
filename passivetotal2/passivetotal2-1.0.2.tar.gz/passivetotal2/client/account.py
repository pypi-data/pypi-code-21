from .baseclient import BaseClient
from .baseclient import iter_not_none


class AccountClient(BaseClient):
    """The Client that hits the Account endpoints of the api

    Most people will generally use the :class:`passivetotal2.client.Client`
    class to access this.

    """
    def get_account(self):
        """function to get account information for the current user.

        Example:

            >>> client = passivetotal2.client.AccountClient()
            >>> client.get_account()
            {
                'firstName': 'John',
                'lastName': 'Smith',
                'fullName': 'John Smith',
                'accountStatus': 'enterprise',
                'admin': True,
                'approvedSources': 'kaspersky, osint, riskiq, virustotal',
                'country': 'united_states',
                'enterpriseUser': 'True',
                'event_code': None,
                'firstActive': '2016-06-20',
                'jobRole': 'other',
                'lastActive': '2017-07-06',
                'organization': 'riskiq',
                'phoneNumber': '555-555-5555',
                'projectPrivateQuotaExceeded': False,
                'projectPublicQuotaExceeded': False,
                'searchApiQuotaExceeded': False,
                'searchWebQuotaExceeded': False,
                'stateOrRegion': 'kansas',
                'suppliedOrganization': 'RiskIQ',
                'user_hash': '000000000000000000000000000000',
                'user_id': '000000000000000000000000000000',
                'username': 'john.smith@riskiq.net',
                'verified': 'True'
            }

        Returns:
            dict: information for the current user"""
        return self.get('/account')

    def get_history(self):
        """function to get account history for the current user.

        Example:

            >>> client = passivetotal2.client.AccountClient()
            >>> client.get_history()
            {
                'history': [
                    {
                        'context': 1,
                        'dt': '2017-06-29 17:00:00',
                        'focus': 'passivetotal.org',
                        'guid': '00000000-0000-0000-0000-000000000000',
                        'source': 'web',
                        'type': 'search',
                        'username': 'john.smith@riskiq.net'
                    },
                    {
                        'context': 1,
                        'dt': '2017-06-29 16:33:07',
                        'focus': 'riskiq.net',
                        'guid': '00000000-0000-0000-0000-000000000000',
                        'source': 'web',
                        'type': 'search',
                        'username': 'john.smith@riskiq.net'
                    }
                ]
            }

        Returns:
            dict: history for the current user"""
        return self.get('/account/history')

    def get_monitors(self):
        return self.get('/account/monitors')

    def get_organization(self):
        """function to get the information for the current user's organization.

        Example:

            >>> client = passivetotal2.client.AccountClient()
            >>> client.get_organization()
            {
                'acceptableDomains':
                    ['riskiq.net', 'passivetotal.org', 'riskiq.com'],
                'active': True,
                'activeMembers': [
                    'john.smith@riskiq.net',
                    'jane.smith@riskiq.net',
                ],
                'admins': [
                    'john.smith@riskiq.net',
                    'jane.smith@riskiq.net',
                ],
                'id': 'riskiq',
                'inactiveMembers': [],
                'lastActive': '2016-11-21 17:31:38',
                'name': 'RiskIQ',
                'registered': '2015-09-21 19:43:49',
                'searchQuota': 999994881,
                'seats': 150,
                'status': 'enterprise',
                'watchQuota': 368.0
            }

        Returns:
            dict: information about the current user's organization"""
        return self.get('/account/organization')

    def get_teamstream(self, source=None, dt=None, type=None, focus=None):
        """Function to get teamstream information.

        Args:
            source (str, optional): Description
            dt (str, optional): Description
            type (str, optional): Description
            focus (str, optional): Description

        Returns:
            dict: Teamstream information
        """
        params = dict(iter_not_none(
            source=source, dt=dt, type=type, focus=focus
        ))
        return self.get('/account/organization/teamstream', params=params)

    def get_quotas(self):
        return self.get('/account/quota')

    def get_sources(self, source=None):
        """Function to get information on sources.

        Example:
            >>> client.get_sources().data
            {
                [
                    {
                        "authRequired": true,
                        "auth": true,
                        "source": "360cn",
                        "description": "360CN is a private source provided by Qihoo, Inc. Users can request access to the source through direct connections.",
                        "label": "360CN",
                        "configuration": {
                            "token_secret": "",
                            "token_key": ""
                        },
                        "website": "http://www.passivedns.cn",
                        "access": [
                            "free",
                            "private"
                        ],
                        "authMethod": {
                            "token_secret": "",
                            "token_key": ""
                        },
                        "active": false,
                        "type": [
                            "pdns"
                        ],
                        "controllable": true
                    },
                    {
                        "authRequired": false,
                        "auth": true,
                        "source": "riskiq",
                        "description": "",
                        "label": "RiskIQ",
                        "configuration": {
                            "token": "",
                            "private_key": ""
                        },
                        "website": "http://www.riskiq.com/",
                        "access": [
                            "commercial"
                        ],
                        "authMethod": {
                            "token": "",
                            "private_key": ""
                        },
                        "active": true,
                        "type": [
                            "pdns"
                        ],
                        "controllable": true
                    }
                ]
            }

        Args:
            source (str, optional): Description

        Returns:
            dict: sources information
        """
        params = {}
        if source is not None:
            params['source'] = source
        return self.get('/account/sources', params=params)

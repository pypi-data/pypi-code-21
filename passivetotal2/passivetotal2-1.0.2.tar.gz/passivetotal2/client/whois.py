from .baseclient import BaseClient


class WhoisClient(BaseClient):
    def get_whois(self, query, compact_record=None):
        """Retrieves whois information using a domain

        Example:
            >>> client.get_whois('example.com').pprint()
            {
                "registered": "1995-08-13T17:00:00.000-0700",
                "tech": {},
                "registryUpdatedAt": "2016-08-13T17:00:00.000-0700",
                "nameServers": [
                    "a.iana-servers.net",
                    "b.iana-servers.net"
                ],
                "registrar": "RESERVED-INTERNET ASSIGNED NUMBERS AUTHORITY",
                "expiresAt": "2017-08-12T17:00:00.000-0700",
                "domain": "example.com",
                "billing": {},
                "telephone": "N/A",
                "organization": "N/A",
                "whoisServer": "whois.example.org",
                "zone": {},
                "registrant": {},
                "lastLoadedAt": "2017-07-01T09:11:24.071-0700",
                "admin": {},
                "name": "N/A"
            }

        Args:
            query (str): domain for the whois query

        Returns:
            dict: whois information
        """
        params = {'query': query}
        if compact_record is not None:
            params['compact_record'] = compact_record
        return self.get('/whois', params=params)

    def get_whois_keyword(self, query):
        """Retrieves whois information using a keyword

        Example:
            >>> client.get_whois_keyword('riskiq').pprint()
            {
                "queryValue": "riskiq",
                "results": [
                    {
                        "fieldMatch": "name",
                        "focusPoint": "riskiq.co.za",
                        "matchType": "domain"
                    },
                    {
                        "fieldMatch": "name",
                        "focusPoint": "riskiq.info",
                        "matchType": "domain"
                    }
                ]
            }

        Args:
            query (str): keyword for the whois query

        Returns:
            dict: whois information
        """
        params = {'query': query}
        return self.get('/whois/search/keyword', params=params)

    def get_whois_search(self, query, field):
        """Searches for whois information using a value and a field

        Args:
            query (str): value for the whois query
            field (str): field to search

                -allowed values:
                    ``email``, ``domain``, ``name``, ``organization``,
                    ``address``, ``phone``, ``nameserver``

        Returns:
            dict: whois information
        """
        params = {'query': query, 'field': field}
        return self.get('/whois/search', params=params)

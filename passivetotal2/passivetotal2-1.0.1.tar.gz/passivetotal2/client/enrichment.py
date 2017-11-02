from .baseclient import BaseClient


class EnrichmentClient(BaseClient):
    def get_enrichment(self, query):
        """Get enrichment data for a domain or IP

        Example:

            >>> client.get_enrichment('example.com').data
            {
                "dynamicDns": false,
                "queryType": "domain",
                "classification": "",
                "everCompromised": false,
                "tag_meta": {
                    "tags": {
                        "created_at": "2017-07-11T19:51:53.697000",
                        "creator": "john.smith@riskiq.net"
                    },
                    "example": {
                        "created_at": "2017-07-11T19:51:51.229000",
                        "creator": "john.smith@riskiq.net"
                    }
                },
                "sinkhole": null,
                "tags": [
                    "example",
                    "tags"
                ],
                "queryValue": "example.com",
                "primaryDomain": "example.com",
                "subdomains": [],
                "tld": ".com"
            }

        Args:
            query (str): the domain or ip to get enrichment data for

        Returns:
            dict: enrichment data
        """
        params = {'query': query}
        return self.get('/enrichment', params=params)

    def get_malware(self, query):
        """Get malware data for a domain or IP

        Example:
            >>> client.get_malware('example.com').data
            {
                "success": true,
                "results": [
                    {
                        "source": "Emerging Threats (Proofpoint)",
                        "sample": "00000000000000000000000000000000",
                        "sourceUrl": "https://threatintel.proofpoint.com/md5/00000000000000000000000000000000",
                        "collectionDate": "2017-06-06 21:59:29"
                    },
                    {
                        "source": "Emerging Threats (Proofpoint)",
                        "sample": "00000000000000000000000000000000",
                        "sourceUrl": "https://threatintel.proofpoint.com/md5/00000000000000000000000000000000",
                        "collectionDate": "2017-07-11 20:00:57"
                    }
                    ]
            }


        Args:
            query (str): the domain or ip to get malware data for

        Returns:
            dict: malware data
        """
        params = {'query': query}
        return self.get('/enrichment/malware', params=params)

    def get_osint(self, query):
        """Get osint data for a domain or IP

        Example:
            >>> client.get_osint('example.com').data
            {
                "results": [
                    {
                        "derived": false,
                        "tags": [
                            "tag",
                            "tags",
                        ],
                        "source": "example.com",
                        "inReport": [
                            "example.info",
                            "example-1.com",
                        ],
                        "sourceUrl": "http://example.example1.com
                    }
                ],
                "success": true
            }


        Args:
            query (str): the domain or ip to get osint data for

        Returns:
            dict: osint data
        """
        params = {'query': query}
        return self.get('/enrichment/osint', params=params)

    def get_subdomains(self, query):
        """Get known subdomains for a domain or IP

        Example:
            >>> client.get_subdomains('example.com').data
            {
                "queryValue": "example.com",
                "success": true,
                "subdomains": [
                    "backup",
                    "bogus",
                    "cdn",
                    "cf-global-posts",
                    "fake",
                    "yoursite"
                ]
            }

        Args:
            query (str): the domain or ip to get known subdomains for

        Returns:
            dict: subdomains
        """
        params = {'query': query}
        return self.get('/enrichment/subdomains', params=params)

    def get_enrichment_bulk(self, queries):
        """Get enrichment data for many domains or IPs

        Args:
            queries (list): the domains or ips to get enrichment data for

        Returns:
            dict: enrichment data
        """
        data = {'query': queries}
        return self.get('/enrichment/bulk', data=data)

    def get_malware_bulk(self, queries):
        """Get malware data for many domains or IPs

        Args:
            queries (list): the domains or ips to get malware data for

        Returns:
            dict: malware data
        """
        data = {'queries': queries}
        return self.get('/enrichment/bulk/malware', data=data)

    def get_osint_bulk(self, queries):
        """Get osint data for many domains or IPs

        Args:
            queries (list): the domains or ips to get osint data for

        Returns:
            dict: osint data
        """
        data = {'query': queries}
        return self.get('/enrichment/bulk/osint', data=data)

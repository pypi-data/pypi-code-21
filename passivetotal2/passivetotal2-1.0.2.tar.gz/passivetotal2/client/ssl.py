from .baseclient import BaseClient


class SSLClient(BaseClient):
    def get_ssl(self, query):
        """Retrieves an SSL certificate by its SHA-1 hash.

        Example:
            >>> client.get_ssl('00000000000000000000000000000000').data
            {
                "issuerSerialNumber": null,
                "subjectCountry": "US",
                "issuerGivenName": null,
                "subjectEmailAddress": null,
                "subjectStateOrProvinceName": "California",
                "issuerCountry": "US",
                "issuerStreetAddress": null,
                "issuerLocalityName": null,
                "issuerProvince": null,
                "subjectLocalityName": "Mountain View",
                "subjectProvince": "California",
                "expirationDate": "Jul 12 00:00:00 2017 GMT",
                "success": true,
                "subjectOrganizationUnitName": null,
                "serialNumber": "7132393951858740153",
                "issuerCommonName": null,
                "issuerOrganizationUnitName": null,
                "subjectOrganizationName": null,
                "issuerStateOrProvinceName": null,
                "issueDate": "Oct 19 09:11:15 2016 GMT",
                "issuerSurname": null,
                "sha1": "00000000000000000000000000000000",
                "subjectSerialNumber": null,
                "subjectSurname": null,
                "fingerprint": "00:0c:0c:f0:00:a0:0a:00:0e:e0:00:e0:0a:0f:0a:e0:0a:00:d0:00",
                "subjectCommonName": "*.apis.example.net",
                "subjectGivenName": null,
                "subjectStreetAddress": null,
                "issuerEmailAddress": null,
                "sslVersion": "3",
                "issuerOrganizationName": null
            }

                    Args:
                        query (str): SHA-1 hash for the cert

        Returns:
            dict: SHA-1 hash information
        """
        params = dict(
            query=query
        )
        return self.get('/ssl-certificate', params=params)

    def get_ssl_history(self, query):
        """Retrieves the history for a SSL certificate by
        SHA-1 hash or IP address.

        Example:
            >>> client.get_ssl_history('00000000000000000000000000000000').data
            {
                "results": [
                    {
                        "lastSeen": "2017-03-06",
                        "firstSeen": "2016-10-24",
                        "sha1": "00000000000000000000000000000000",
                        "ipAddresses": [
                            "000.000.000.000",
                            "000.000.00.00",
                        ]
                    }
                ],
                "success": true
            }


        Args:
            query (str): SHA-1 or IP address for the cert

        Returns:
            dict: SHA-1 hash history information
        """
        params = dict(
            query=query
        )
        return self.get('/ssl-certificate/history', params=params)

    def get_ssl_by_keyword(self, query):
        """Retrieves a SHA-1 hash using a keyword

        Example:

            >>> client.get_ssl_by_keyword(example).data
            {
                "results": [
                    {
                        "focusPoint": "00000000000000000000000000000000",
                        "matchType": "sha1",
                        "fieldMatch": "certificate"
                    },
                    {
                        "focusPoint": "00000000000000000000000000000000",
                        "matchType": "sha1",
                        "fieldMatch": "certificate"
                    },
                ],
                "queryValue": "example",
                "success": true
            }

        Args:
            query (str): keyword for the SHA-1 hash

        Returns:
            dict: SHA-1 hash information
        """
        params = dict(
            query=query
        )
        return self.get('/ssl-certificate/search/keyword', params=params)

    def search_ssl(self, query, field):
        """Searches for a SHA-1 hash using a value and a field

        Args:
            query (str): value for the search
            field (str): field to search

                - Allowed values:
                    ``issuerSurname``, ``subjectOrganizationName``,
                    ``issuerCountry``, ``issuerOrganizationUnitName``,
                    ``fingerprint``, ``subjectOrganizationUnitName``,
                    ``serialNumber``, ``subjectEmailAddress``,
                    ``subjectCountry``, ``issuerGivenName``,
                    ``subjectCommonName``, ``issuerCommonName``,
                    ``issuerStateOrProvinceName``, ``issuerProvince``,
                    ``subjectStateOrProvinceName``, ``sha1``,
                    ``subjectStreetAddress``, ``subjectSerialNumber``,
                    ``issuerOrganizationName``, ``subjectSurname``,
                    ``subjectLocalityName``, ``issuerStreetAddress``,
                    ``issuerLocalityName``, ``subjectGivenName``,
                    ``subjectProvince``, ``issuerSerialNumber``,
                    ``issuerEmailAddress``

        Returns:
            dict: SHA-1 hash information


        """
        params = dict(
            query=query, field=field
        )
        return self.get('/ssl-certificate/search', params=params)

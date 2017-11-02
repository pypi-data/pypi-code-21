from .baseclient import BaseClient, iter_not_none


class HostClient(BaseClient):
    def get_host_attributes(self, query, start=None, end=None):
        """Retrieves host attribute components for a domain or IP

        Example:
            >>> client.get_host_attributes('example.com').data
            {
                "success": true,
                "totalRecords": 2,
                "results": [
                    {
                        "firstSeen": "2016-05-07 02:28:09",
                        "label": "ECSF (cpm/F9CF)",
                        "lastSeen": "2017-01-02 19:46:15",
                        "version": null,
                        "hostname": "example.com",
                        "category": "Server"
                    },
                    {
                        "firstSeen": "2016-12-19 17:33:32",
                        "label": "ECSF (den/1DA1)",
                        "lastSeen": "2016-12-20 17:41:11",
                        "version": null,
                        "hostname": "example.com",
                        "category": "Server"
                    }
                ]
            }

        Args:
            query (str): Domain or IP to retrieve host attribute components for
            start (str, optional): start datetime
            end (str, optional): end datetime

        Returns:
            dict: host attribute components
        """
        params = dict(iter_not_none(
            query=query, start=start, end=end
        ))
        return self.get('/host-attributes/components', params=params)

    def get_host_attributes_pairs(self, query, direction, start=None, end=None):
        """Retrieves host attribute pairs for a domain or IP

        Args:
            query (str): Domain or IP to retrieve host attribute pairs for
            direction (str): the direction to query in

                - allowed values are ``children`` and ``parents``
            start (str, optional): start datetime
            end (str, optional): end datetime

        Returns:
            dict: host attribute pairs
        """
        params = dict(iter_not_none(
            query=query, direction=direction, start=start, end=end
        ))
        return self.get('/host-attributes/pairs', params=params)

    def get_host_attributes_trackers(self, query, start=None, end=None):
        """Retrieves host attribute trackers for a domain or IP

        Example:
            >>> client.get_host_attributes_trackers('google.com').data
            {
                "totalRecords": 2,
                "results": [
                    {
                        "lastSeen": "2017-06-01 19:04:28",
                        "firstSeen": "2016-08-09 07:23:58",
                        "attributeType": "example",
                        "hostname": "www.example.com",
                        "attributeValue": "value"
                    },
                    {
                        "lastSeen": "2015-01-24 07:00:53",
                        "firstSeen": "2014-12-09 02:12:03",
                        "attributeType": "example",
                        "hostname": "www.example.com",
                        "attributeValue": "value"
                    }
                ],
                "success": true
            }


        Args:
            query (str): Domain or IP to retrieve host attribute trackers for
            start (str, optional): start datetime
            end (str, optional): end datetime

        Returns:
            dict: host attribute trackers
        """
        params = dict(iter_not_none(
            query=query, start=start, end=end
        ))
        return self.get('/host-attributes/trackers', params=params)

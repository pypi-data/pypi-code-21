from .baseclient import BaseClient


class ActionsClient(BaseClient):
    def get_tags(self, query):
        """Function to get tags for an artifact.

        Args:
            query (str): Artifact to get tags for

        Returns:
            dict: current tags
        """
        params = {'query': query}
        return self.get('/actions/tags', params=params)

    def add_tags(self, query, tags):
        """function to add tags to an artifact

        Args:
            query (str): Artifact to add tags to
            tags (str): Tags to add

        Returns:
            dict: new tags for artifact
        """
        data = {'query': query, 'tags': tags}
        return self.post('/actions/tags', data=data)

    def set_tags(self, query, tags):
        """function to set tags for an artifact

        Args:
            query (str): Artifact to set tags on
            tags (str): Tags to set

        Returns:
            dict: new tags for artifact
        """
        data = {'query': query, 'tags': tags}
        return self.put('/actions/tags', data=data)

    def delete_tags(self, query, tags):
        """function to delete tags from an artifact

        Args:
            query (str): Artifact to delete tags from
            tags (str): Tags to set

        Returns:
            dict: new tags for artifact
        """
        data = {'query': query, 'tags': tags}
        return self.delete('/actions/tags', data=data)

    def search_tags(self, query):
        """function to search for user tags on an artifact

        Args:
            query (str): tag to search for

        Returns:
            dict: artifacts with that tag
        """
        params = {'query': query}
        return self.get('/actions/tags/search', params=params)

    def get_classification(self, query):
        """function to get the classification status for a domain
        do not iterate through domains using this
        function, use :func:`get_classification_bulk` instead

        Args:
            query (str): domain to get classification status of

        Returns:
            dict: classification of that domain
        """
        params = {'query': query}
        return self.get('/actions/classification', params=params)

    def get_classification_bulk(self, queries):
        """function to get the classification status for many domains

        Args:
            queries (list): domains to get classification status of

        Returns:
            dict: classification of those domains
        """
        data = {'query': queries}
        return self.get('/actions/bulk/classification', data=data)

    def set_classification(self, query, classification):
        """function to set the classification status for a domain

        Args:
            query (str): domain to set classification status of
            classification (str): Classification status\n
                - Allowed values: ``malicious``, ``suspicious``,
                    ``non-malicious``, ``unknown``

        Returns:
            dict: new classification of that domain
        """
        data = {'query': query, 'classification': classification}
        return self.post('/actions/classification', data=data)

    def set_classification_bulk(self, queries, classification):
        """function to set the classification status for a domain

        Args:
            queries (list): domains to set classification status of
            classification (str): Classification status\n
                - Allowed values: ``malicious``, ``suspicious``,
                    ``non-malicious``, ``unknown``

        Returns:
            dict: new classification of that domain
        """
        results = []
        for query in queries:
            data = {'query': query, 'classification': classification}
            results.append(self.post('/actions/classification', data=data))
        return results

    def get_compromised(self, query):
        """function to get compromised status for a domain

        Args:
            query (str): domain to get compromised status of

        Returns:
            dict: compromised status of that domain
        """
        params = {'query': query}
        return self.get('/actions/ever-compromised', params=params)

    def set_compromised(self, query, status):
        """function to set compromised status for a domain

        Args:
            query (str): domain to get compromised status of
            status (bool): compromised status of the domain

        Returns:
            dict: new compromised status of that domain
        """
        data = {'query': query, 'status': status}
        return self.post('/actions/ever-compromised', data=data)

    def get_dynamic_dns(self, query):
        """function to get the dynamic dns status for a domain

        Indicates whether or not a domain's DNS
        records are updated via dynamic DNS

        Args:
            query (str): domain to get dynamic dns status of

        Returns:
            dict: dynamic dns status of that domain
        """
        params = {'query': query}
        return self.get('/actions/dynamic-dns', params=params)

    def set_dynamic_dns(self, query, status):
        """function to set the dynamic dns status for a domain

        Args:
            query (str): domain to get dynamic dns status of
            status (bool): new dynamic dns status

        Returns:
            dict: new dynamic dns status of that domain
        """
        data = {'query': query, 'status': status}
        return self.post('/actions/dynamic-dns', data=data)

    def get_sinkhole(self, query):
        """function to get the sinkhole status for an IP address

        Indicates whether or not an IP address is a sinkhole.

        Args:
            query (str): IP address to get sinkhole status of

        Returns:
            dict: sinkhole status of that IP address
        """
        params = {'query': query}
        return self.get('/actions/sinkhole', params=params)

    def set_sinkhole(self, query, status):
        """function to set the sinkhole status for an IP address

        Args:
            query (str): IP address to get sinkhole status of
            status (bool): new sinkhole status

        Returns:
            dict: new sinkhole status of that IP address
        """
        data = {'query': query, 'status': status}
        return self.post('/actions/sinkhole', data=data)

    def get_monitor(self, query):
        params = {'query': query}
        return self.get('/actions/monitor', params=params)

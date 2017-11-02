from .baseclient import BaseClient, iter_not_none


class DNSClient(BaseClient):
    def get_dns_passive(self, query, timeout=7, start=None, end=None):
        """Retrieves the passive DNS results from active account sources

        Args:
            query (str): Domain or IP to retrieve PDNS for
            timeout (str, optional): timeout for external resources
            start (str, optional): start datetime
            end (str, optional): end datetime

        Returns:
            dict: PDNS information
        """
        params = dict(iter_not_none(
            query=query, timeout=timeout, start=start, end=end
        ))
        return self.get('/dns/passive', params=params)

    def get_dns_unique(self, query, timeout=None, start=None, end=None):
        """Retrieves unique passive DNS results from active account sources

        Args:
            query (str): Domain or IP to retrieve PDNS for
            timeout (str, optional): timeout for external resources
            start (str, optional): start datetime
            end (str, optional): end datetime

        Returns:
            dict: PDNS information
        """
        params = dict(iter_not_none(
            query=query, timeout=timeout, start=start, end=end
        ))
        return self.get('/dns/passive/unique', params=params)

    def get_dns_keyword(self, query):
        """Retrieves passive DNS results for a keyword query

        Args:
            query (str): keyword to query with

        Returns:
            dict: PDNS information
        """
        params = {'query': query}
        return self.get('/dns/search/keyword', params=params)

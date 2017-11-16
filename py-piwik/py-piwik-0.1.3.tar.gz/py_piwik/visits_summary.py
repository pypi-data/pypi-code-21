from py_piwik.helpers import _finalize_args
import requests
import logging

log = logging.getLogger('py_piwik/visits_summary')


class VisitsSummary(object):
    def __init__(self, url: str, token: str):
        """
        Provides Access to the API Module SitesManager
        """
        self.url = url
        self.token = token

    def get(self):
        raise NotImplemented

    def get_visits(self, args: dict) -> dict:
        """
        Returns value of total visitor count for idSite with date and period

        :param args: API Arguments
        :return: visitor count
        """
        if 'idSite' not in args:
            raise ValueError('Missing required argument args[\'idSite\']')

        if 'period' not in args:
            raise ValueError('Missing required argument args[\'period\']')

        if 'date' not in args:
            raise ValueError('Missing required argument args[\'date\']')

        fargs = _finalize_args(args, self.token, 'VisitsSummary.getVisits')

        try:
            results = requests.get(self.url, params=args)
            log.debug(self.url)
        except ConnectionError as err:
            log.error(err)
            raise err
        else:
            if not results.ok:
                log.debug(results)
                raise requests.HTTPError
            return results.json()

    def get_unique_visitors(self, args: dict) -> dict:
        """
        Return value of unique visitor count for idSite with date and period

        :param args: API ArgumentsVisitsSummary.getVisits

        :return: unique visitor count
        """

        if 'idSite' not in args:
            raise ValueError('Missing required argument args[\'idSite\']')

        if 'period' not in args:
            raise ValueError('Missing required argument args[\'period\']')

        if 'date' not in args:
            raise ValueError('Missing required argument args[\'date\']')

        fargs = _finalize_args(args, self.token, 'VisitsSummary.getUniqueVisitors')

        try:
            results = requests.get(self.url, params=fargs)
            log.debug(results.url)
        except ConnectionError as err:
            log.error(err)
            raise err
        else:
            if not results.ok:
                log.debug(results)
                raise requests.HTTPError
            return results.json()

    def get_users(self):
        raise NotImplemented

    def get_actions(self):
        raise NotImplemented

    def get_max_actions(self):
        raise NotImplemented

    def get_bounce_count(self):
        raise NotImplemented

    def get_visits_converted(self):
        raise NotImplemented

    def get_sum_visits_length(self):
        raise NotImplemented

    def get_sum_visits_length_pretty(self):
        raise NotImplemented

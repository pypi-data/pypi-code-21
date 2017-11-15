from py_piwik.helpers import _url, _finalize_args
import requests
import logging

log = logging.getLogger('py_piwik/goals')


class Goals(object):

    def __init__(self, url: str, token: str):
        """
        Provides Access to the API Module Goals
        """
        self.url = url
        self.token = token

    def get_goal(self):
        raise NotImplemented

    def get_goals(self):
        raise NotImplemented

    def add_goal(self):
        raise NotImplemented

    def update_goal(self):
        raise NotImplemented

    def delete_goal(self):
        raise NotImplemented

    def get_item_sku(self):
        raise NotImplemented

    def get_item_name(self):
        raise NotImplemented

    def get_item_category(self):
        raise NotImplemented

    def get(self, args: dict) -> dict:
        """
        Return data related to a goal

        Example Results:
        {
            "nb_conversions":0,
            "nb_visits_converted":0,
            "revenue":0,"conversion_rate":"0%",
            "nb_conversions_new_visit":0,
            "nb_visits_converted_new_visit":0,
            "revenue_new_visit":0,
            "conversion_rate_new_visit":"0%",
            "nb_conversions_returning_visit":0,
            "nb_visits_converted_returning_visit":0,
            "revenue_returning_visit":0,
            "conversion_rate_returning_visit":"0%"
        }

        :param args: api arguments
        :type args: dict

        :return: goal data
        :type return: dict
        """

        if 'idSite' not in args:
            raise ValueError('Missing required argument args[\'idSite\']')
        if 'period' not in args:
            raise ValueError('Missing required argument args[\'period\']')
        if 'date' not in args:
            raise ValueError('Missing required argument args[\'date\']')

        fargs = _finalize_args(args)
        fargs['token_auth'] = self.token
        fargs['method'] = 'Goals.get'

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

    def get_days_to_conversion(self):
        raise NotImplemented

    def get_visits_until_conversion(self):
        raise NotImplemented

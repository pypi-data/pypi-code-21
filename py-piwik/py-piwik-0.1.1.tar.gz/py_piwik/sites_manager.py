from py_piwik.helpers import _finalize_args
import requests
import logging

log = logging.getLogger('py_piwik/sites_manager')


class SitesManager(object):

    def __init__(self, url: str, token: str):
        """
        Provides Access to the API Module SitesManager
        """
        self.url = url
        self.token = token

    def get_javascript_tag(self):
        raise NotImplemented

    def get_image_tracking_code(self):
        raise NotImplemented

    def get_sites_from_group(self):
        raise NotImplemented

    def get_sites_group(self):
        raise NotImplemented

    def get_site_from_id(self):
        raise NotImplemented

    def get_site_urls_from_id(self, args: dict) -> list:
        """
        Return a list of urls from a siteID

        :param args: api arguments
        :type args: dict

        :return: url list
        :type return: list
        """

        if 'idSite' not in args:
            raise ValueError('Missing required argument args[\'idSite\']')

        fargs = _finalize_args(args)
        fargs['token_auth'] = self.token
        fargs['method'] = 'SitesManager.getSiteUrlsFromId'

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

    def get_all_sites(self):
        raise NotImplemented

    def get_all_sites_id(self):
        raise NotImplemented

    def get_sites_with_admin_access(self):
        raise NotImplemented

    def get_sites_with_view_access(self):
        raise NotImplemented

    def get_sites_with_at_least_view_access(self):
        raise NotImplemented

    def get_sites_id_with_admin_access(self):
        raise NotImplemented

    def get_sites_id_with_view_access(self):
        raise NotImplemented

    def get_sites_id_with_at_least_view_access(self):
        raise NotImplemented

    def get_sites_id_from_site_url(self):
        raise NotImplemented

    def add_site(self):
        raise NotImplemented

    def get_site_settings(self):
        raise NotImplemented

    def delete_site(self):
        raise NotImplemented

    def add_site_alias_urls(self):
        raise NotImplemented

    def set_site_alias_urls(self):
        raise NotImplemented

    def get_ips_for_range(self):
        raise NotImplemented

    def set_global_excluded_ips(self):
        raise NotImplemented

    def set_global_search_parameters(self):
        raise NotImplemented

    def get_search_keyword_parameters_global(self):
        raise NotImplemented

    def get_search_category_parameters_global(self):
        raise NotImplemented

    def get_excluded_query_parameters_global(self):
        raise NotImplemented

    def get_excluded_user_agents_global(self):
        raise NotImplemented

    def set_global_excluded_user_agents(self):
        raise NotImplemented

    def is_site_specific_user_agent_excluded_enabled(self):
        raise NotImplemented

    def set_site_specific_user_agent_excluded_enabled(self):
        raise NotImplemented

    def get_keep_url_fragments_global(self):
        raise NotImplemented

    def set_keep_url_fragments_global(self):
        raise NotImplemented

    def set_global_excluded_query(self):
        raise NotImplemented

    def set_global_excluded_query_parameters(self):
        raise NotImplemented

    def get_excluded_ips_global(self):
        raise NotImplemented

    def get_default_currency(self):
        raise NotImplemented

    def set_default_currency(self):
        raise NotImplemented

    def get_default_timezone(self):
        raise NotImplemented

    def set_default_timezone(self):
        raise NotImplemented

    def update_site(self):
        raise NotImplemented

    def get_currency_list(self):
        raise NotImplemented

    def get_currency_symbols(self):
        raise NotImplemented

    def is_timezone_support_enabled(self):
        raise NotImplemented

    def get_timezone_list(self):
        raise NotImplemented

    def get_unique_site_timezones(self):
        raise NotImplemented

    def rename_group(self):
        raise NotImplemented

    def get_pattern_match_sites(self):
        raise NotImplemented

    def get_num_websites_to_display_per_page(self):
        raise NotImplemented

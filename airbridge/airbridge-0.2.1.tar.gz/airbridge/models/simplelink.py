#-*- coding: utf-8 -*-
from sqlalchemy.sql import text
from sqlalchemy import exc
from enum import Enum
from urlparse import urlparse, parse_qsl, urlunparse
from urllib import urlencode, quote, unquote
from airbridge.models.app_resource import AppResource
from airbridge.utils.tools import is_empty, get_subdomain_detached_url, \
                                  drop_bypass_params, get_path_list_from_url, \
                                  get_md5_hash, get_url_with_sorted_params, \
                                  ret_one_row_without_exception, \
                                  have_front_atsign, detach_front_atsign, \
                                  parse_long_url_for_simplelink, \
                                  get_https_market_url, \
                                  get_native_market_url, \
                                  get_market_url_with_params, \
                                  get_time_stamp, get_query_string_as_dict, \
                                  get_utm_params, quote_referrer_param, \
                                  remove_parameter_from_url, \
                                  get_url_with_additional_params, \
                                  is_external_scraper, get_client_info_from_request_object, \
                                  send_work_to_queue


class Simplelink():

    class FoundBy(Enum):
        NOT_FOUND = 0
        APP_NAME = 1
        SHORT_ID = 2
        LONG_URL = 3

    def __init__(self, read_engine, long_url, engine=None):

        self.read_engine = read_engine 
        self.engine = engine if engine is not None else read_engine

        self.found_by = self.FoundBy.NOT_FOUND
        self.app = {}
        self.app_resource = None
        self.short_id = ""
        self.long_url = long_url
        self.sl_type = 0
        self.long_url_params = {
            "label": None,
            "campaign": None,
            "ad_group": None,
            "ad_creative": None,
            "medium": None,
            "term": None,
            "content": None,

            "tracking_template_id": None,
            "curl_id": None,
            "routing_short_id": None,
            "sms": None,
            "fallback": None,
            "custom_landing_url": None,
        }
        self.dynamic_params = {}
        self.og_tag_id = None
        self.deeplink_params_id = None

        # Attribution data
        self.touch_timestamp = get_time_stamp(time_format='milli')
        self.ret_app_data(long_url)

    def ret_app_data(self, long_url):
        """ Get app table data from database and set object.app property. """

        # Get/create short link for this s. trailing url.
        try:
            sub_path = get_path_list_from_url(long_url)[0]
        except:
            raise Exception('No app name or short_id is provided. (Wrong url format)')

        # Query to get app data
        query_str = """
                    SELECT
                        short_id,
                        app_id,
                        label,
                        campaign,
                        ad_group,
                        tracking_template_id,
                        ad_creative,
                        medium,
                        term,
                        content,
                        long_url,
                        sl_type,
                        long_url_hash,
                        og_tag_id,
                        deeplink_params_id,
                        created_at

                    FROM
                        tbl_sl_mappings

                    WHERE
                        short_id=:short_id
                    """

        # Assume that sub_path is short_id
        args = {
            'short_id': sub_path
        }

        # To get app data with long_url_hash
        if long_url != None:
            long_url_hash = get_md5_hash(get_url_with_sorted_params(long_url))
            query_str += ' OR long_url_hash = :long_url_hash'
            args['long_url_hash'] = long_url_hash

        # Execute query
        rows = self.read_engine.execute(text(query_str), args)
        self.short_link = ret_one_row_without_exception(rows)

        # short_id, long_url로 못 찾았다.
        if self.short_link == None:
            if have_front_atsign(sub_path):
                # this is app name
                app_name = detach_front_atsign(sub_path)
                self.app_resource = AppResource(subdomain=app_name, engine=self.engine, read_engine=self.read_engine)
                self.app = self.app_resource.app
                self.found_by = self.FoundBy.APP_NAME
            else:
                raise Exception("No short link.{}".format(sub_path))

        # short_id, long_url로 찾았다.
        else:
            self.app_resource = AppResource(app_id=self.short_link['app_id'], engine=self.engine, read_engine=self.read_engine)
            self.app = self.app_resource.app
            self.long_url = self.short_link['long_url']
            self.og_tag_id = self.short_link['og_tag_id']
            self.deeplink_params_id = self.short_link['deeplink_params_id']
            self.short_id = self.short_link['short_id']
            self.label = self.short_link['label']
            self.sl_type = self.short_link['sl_type']
            self.set_params_from_long_url(self.long_url)

            # long url일땐 subpath가 @가 붙었을거라 생각했다.
            if have_front_atsign(sub_path):
                self.found_by = self.FoundBy.LONG_URL
            else:
                self.found_by = self.FoundBy.SHORT_ID

    def send_stats(self, queue, request, target_link, event_category, sdk_version, client_id, transaction_id, ad_click_id=None):

        if is_external_scraper(request):
            return

        client = get_client_info_from_request_object(request, request.url)
        self.touch_timestamp = self.dynamic_params.get('abmacro_dynamic_timestamp') or self.touch_timestamp

        send_work_to_queue(queue_session=queue, 
                           queue_name="airbridge-emergency-queue",
                           what_to_do='set_stat_simple_link', 
                           platform_type=u'sl', 
                           event_category=event_category,
                           app_id=self.app['app_id'],
                           short_id=self.short_id,
                           origin_url=request.url,
                           ad_click_id=ad_click_id or self.dynamic_params.get('abmacro_dynamic_ad_id'),
                           transaction_id=transaction_id,
                           client_id=client_id or client.get('client_id'),
                           client_ip=client.get('client_ip'),
                           user_type=client.get('client_type'),
                           udl_history=client.get('client_history'),
                           user_agent=client.get('client_ua'),
                           referer_url=request.referrer,
                           social_referer_type=client.get('social'),
                           target=client.get('client_device'),
                           request_timestamp=self.touch_timestamp,
                           store_url=target_link,
                           sdk_version=sdk_version)

    def get_short_url(self):
        short_url = "http://{0}/".format(opt['short_host']) + self.short_id
        return short_url

    def get_long_url(self):
        return self.long_url

    def found_by_short_id(self):
        return self.found_by == self.FoundBy.SHORT_ID

    def found_by_app_name(self):
        return self.found_by == self.FoundBy.APP_NAME

    def found_by_long_url(self):
        return self.found_by == self.FoundBy.LONG_URL

    def set_params_from_long_url(self, long_url):
        """ Extract 5 parameters from long url.

        long_url format
        => http(s)://abr.ge/<app_name>/<label>?campaign=<campaign>&term=<term>&medium=<medium>&content=<content>
        """

        app_name, label, queries = parse_long_url_for_simplelink(long_url)
        for key, value in queries:
            if key == 'campaign' or \
                key == 'term' or \
                key == 'ad_group' or \
                key == 'tracking_template_id' or \
                key == 'ad_creative' or \
                key == 'medium' or \
                key == 'content' or \
                key == 'sms' or \
                key == 'fallback' or \
                key == 'curl_id':
                self.long_url_params[key] = value

            elif key == 'custom_landing_url':
                if value is not None and "%3A//" in value:
                    self.long_url_params[key] = unquote(value)
                else:
                    self.long_url_params[key] = value

        self.long_url_params['label'] = label
        self.long_url = long_url

        return self.long_url_params

    def get_params_from_long_url(self):
        return self.long_url_params

    def get_airbridge_query(self, client_id, additional_query={}, tid=None, ad_click_id=None):

        long_url_params = self.get_params_from_long_url()

        params_dict = {}
        params_dict['airbridge'] = 'true'
        params_dict['transaction_id'] = client_id
        params_dict['short_id'] = self.short_id
        params_dict['referrer_timestamp'] = str(self.touch_timestamp)

        if tid is not None:
            params_dict['airbridge_tid'] = tid

        if ad_click_id is not None:
            params_dict['ad_click_id'] = ad_click_id

        return params_dict

    def get_android_market_url_with_referrer(self, client_id, additional_query={}, tid=None, ad_click_id=None):
        market_url = self.app['android_market']
        query = self.get_airbridge_query(client_id, additional_query, tid, ad_click_id)

        if is_empty(market_url):
            return None

        url_with_referrer = get_market_url_with_params(market_url, query)
        url_with_referrer = quote_referrer_param(url_with_referrer)
        return get_https_market_url(url_with_referrer)

    def get_ios_store_url(self):
        return get_https_market_url(self.app['ios_market'])


def create_new_simplelink(url, read_engine, engine=None):

    if is_empty(url): #pragma: no cover
        raise Exception('No url is provided (create_new_simplelink)')

    # detach s. subdomain
    url = get_subdomain_detached_url(url)

    # detach *dynamic* parameters
    url, dynamic_params = drop_bypass_params(url, 'dynamic')

    simplelink = Simplelink(read_engine=read_engine, engine=engine, long_url=url)
    simplelink.dynamic_params = dynamic_params

    # TODO Custom Domain Mismatch
    # TODO simplelink.found_by_app_name() => create new simplelink
    return simplelink

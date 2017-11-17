from py_piwik.sites_manager import *
import responses
from os import environ

testing_url = 'https://piwik.testing/index.php'
testing_token = '1234567890'

client = SitesManager(testing_url, testing_token)

@responses.activate
def test_get_site_urls_from_id():
    res_json = [
        {
            "idsite": "12",
            "name": "CBD",
            "main_url": "https://tryoilhemp.com",
            "ts_created": "2017-09-13 00:00:00",
            "ecommerce": "0",
            "sitesearch": "1",
            "sitesearch_keyword_parameters": "",
            "sitesearch_category_parameters": "",
            "timezone": "America/Denver",
            "currency": "USD",
            "exclude_unknown_urls": "0",
            "excluded_ips": "",
            "excluded_parameters": "",
            "excluded_user_agents": "",
            "group": "",
            "type": "website",
            "keep_url_fragment": "0"
        }
    ]

    responses.add(responses.Response(
        method='GET',
        url=testing_url+'?idSite=12&format=JSON&module=API&token_auth='+ testing_token + '&method=SitesManager.getSiteUrlsFromId',
        match_querystring=True,
        json=res_json
    ))

    args = {
        'idSite': str(12)
    }

    res = client.get_site_urls_from_id(args)

    assert res == [
        {
            "idsite": "12",
            "name": "CBD",
            "main_url": "https://tryoilhemp.com",
            "ts_created": "2017-09-13 00:00:00",
            "ecommerce": "0",
            "sitesearch": "1",
            "sitesearch_keyword_parameters": "",
            "sitesearch_category_parameters": "",
            "timezone": "America/Denver",
            "currency": "USD",
            "exclude_unknown_urls": "0",
            "excluded_ips": "",
            "excluded_parameters": "",
            "excluded_user_agents": "",
            "group": "",
            "type": "website",
            "keep_url_fragment": "0"
        }
    ]

# -*- coding: UTF-8 -*-
"""
Module for loading/scraping data from the web
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "the01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2014-17, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.9"
__date__ = "2017-11-03"
# Created: 2014-04-02 11:23

import re
import socket

from bs4 import BeautifulSoup
import html2text
import requests
from requests import HTTPError
from requests.exceptions import SSLError, Timeout, ConnectionError

from flotils.loadable import Loadable

from .default_user_agents import default_user_agents
from .models import Response, CacheInfo
from .cache import FileCache, NullCache


class WEBParameterException(Exception):
    """ Parameter Exception """
    pass


class WEBFileException(IOError):
    """ File Exception """
    pass


class WEBConnectException(Exception):
    """ Error with web connection """
    pass


class WebScraper(Loadable):
    """ Class for cached, session get/post/.. with optional scraping """

    def __init__(self, settings=None):
        """
        Initialize object

        :param settings: Settings for instance (default: None)
        :type settings: dict | None
        :rtype: None
        """
        if settings is None:
            settings = {}
        super(WebScraper, self).__init__(settings)

        self.url = settings.get('url', None)
        self.scheme = settings.get('scheme', None)
        self.timeout = settings.get('timeout', None)

        cache_sett = settings.get('cache')
        self.cache = NullCache()
        """ :type : None | floscraper.cache.Cache """
        if cache_sett:
            self.cache = FileCache(cache_sett)

        self._auth_method = settings.get('auth_method', None)
        self._auth_username = settings.get('auth_username', None)
        self._auth_password = settings.get('auth_password', None)

        self.session = None
        """ object to do http actions
            :type _br: requests.Session """
        self._handle_redirect = settings.get('handle_redirect', True)

        agent_browser = default_user_agents['browser']['keith']
        agent_os = default_user_agents['os']['linux_i686']
        agent = settings.get('user_agent', None)

        if "default_user_agents_browser" in settings:
            brow = settings['default_user_agents_browser']
            agent_browser = default_user_agents['browser'].get(brow, None)
        if "default_user_agents_os" in settings:
            os = settings['default_user_agents_os']
            agent_os = default_user_agents['os'].get(os, None)
        if "user_agent_browser" in settings:
            agent_browser = settings['user_agent_browser']
        if "user_agent_os" in settings:
            agent_os = settings['user_agent_os']

        if not agent:
            if agent_browser and agent_os:
                agent = agent_browser.format(agent_os)
        self.user_agent = agent
        self._text_maker = None
        """ object to translate html to markdown (html2text)
            :type : None | html2text.HTML2Text """
        if settings.get('html2text'):
            self._set_html2text(settings['html2text'])
        self.html_parser = settings.get('html_parser', "html.parser")
        """ what html parser to use (default: html.parser - built in)
            :type : str | unicode """

    def _browser_init(self):
        """
        Init the browsing instance if not setup

        :rtype: None
        """
        if self.session:
            return

        self.session = requests.Session()
        headers = {}

        if self.user_agent:
            headers['User-agent'] = self.user_agent
        self.session.headers.update(headers)

        if self._auth_method in [None, "", "HTTPBasicAuth"]:
            if self._auth_username is not None:
                self.session.auth = (self._auth_username, self._auth_password)

    def _set_html2text(self, settings):
        """
        Load settings for html2text (https://github.com/Alir3z4/html2text)

        Warning: does not check options/values

        :param settings: Settings for the object
            (see:https://github.com/Alir3z4/html2text/blob/master/docs/usage.md)
        :type settings: dict
        :rtype: None
        """
        self._text_maker = html2text.HTML2Text()
        for param in settings:
            if not hasattr(self._text_maker, param):
                raise WEBParameterException(
                    "Setting html2text failed - unknown parameter {}".format(
                        param
                    )
                )
            setattr(self._text_maker, param, settings[param])

    def load_scrap(self, path):
        """
        Load scraper settings from file

        :param path: Path to file
        :type path: str
        :rtype: None
        :raises WEBFileException: Failed to load settings
        :raises WEBParameterException: Missing parameters in file
        """
        try:
            conf = self.load_settings(path)
        except:
            # Should only be IOError
            self.exception("Failed to load file")
            raise WEBFileException("Failed to load from {}".format(path))

        if "scheme" not in conf:
            raise WEBParameterException("Missing scheme definition")
        if "url" not in conf:
            raise WEBParameterException("Missing url definition")
        version = conf.get('version', None)
        if version != "1.0":
            raise WEBParameterException(
                "Unsupported version {}".format(version)
            )
        self.scheme = conf['scheme']
        self.url = conf['url']
        self.timeout = conf.get('timeout', self.timeout)
        if conf.get('html2text'):
            self._set_html2text(conf['html2text'])

    def request(
            self, method, url, timeout=None,
            headers=None, data=None, params=None
    ):
        """
        Make a request using the requests library

        :param method: Which http method to use (GET/POST)
        :type method: str | unicode
        :param url: Url to make request to
        :type url: str | unicode
        :param timeout: Timeout for request (default: None)
            None -> infinite timeout
        :type timeout: None | int | float
        :param headers: Headers to be passed along (default: None)
        :type headers: None | dict
        :param data: Data to be passed along (e.g. body in POST)
            (default: None)
        :type data: None | dict
        :param params: Parameters to be passed along (e.g. with url in GET)
            (default: None)
        :type params: None | dict
        :return: Response to the request
        :rtype: requests.Response
        :raises WEBConnectException: Loading failed
        """
        if headers is None:
            headers = {}
        if not self.session:
            self._browser_init()

        try:
            response = self.session.request(
                method,
                url,
                timeout=timeout,
                allow_redirects=self._handle_redirect,
                headers=headers,
                data=data,
                params=params
            )
        except SSLError as e:
            raise WEBConnectException(e)
        except HTTPError:
            raise WEBConnectException("Unable to load {}".format(url))
        except (Timeout, socket.timeout):
            raise WEBConnectException("Timeout loading {}".format(url))
        except ConnectionError:
            raise WEBConnectException("Failed to load {}".format(url))
        except Exception:
            self.exception("Failed to load {}".format(url))
            raise WEBConnectException(
                "Unknown failure loading {}".format(url)
            )
        return response

    def _get(self, url, **kwargs):
        """
        Make GET request

        :param url: Url to make the request to
        :type url: str | unicode
        :param kwargs: See _requests for parameters
        :type kwargs:
        :return: Response
        :rtype: requests.Response
        """
        return self.request("GET", url, **kwargs)

    def _post(self, url, **kwargs):
        """
        Make POST request

        :param url: Url to make the request to
        :type url: str | unicode
        :param kwargs: See _requests for parameters
        :type kwargs: dict
        :return: Response
        :rtype: requests.Response
        """
        return self.request("POST", url, **kwargs)

    def get(self, url, timeout=None, headers=None, params=None, cache_ext=None):
        """
        Make get request to url (might use cache)

        :param url: Url to make request to
        :type url: str | unicode
        :param timeout: Timeout for request (default: None)
            None -> infinite timeout
        :type timeout: None | int | float
        :param headers: Headers to be passed along (default: None)
        :type headers: None | dict
        :param params: Parameters to be passed along with url (default: None)
        :type params: None | dict
        :param cache_ext: External cache info
        :type cache_ext: floscraper.models.CacheInfo
        :return: Response
        :rtype: floscraper.models.Response | None
        :raises WEBConnectException: Loading failed
        """
        if headers is None:
            headers = {}
        cached = cache_info = None
        # TODO: add params to caching key
        if self.cache:
            cached, cache_info = self.cache.get(url)

        if cache_ext:
            # Check local cache
            if not cache_info:
                cache_info = cache_ext
            if cache_info.access_time and cache_ext.access_time:
                if cache_info.access_time < cache_ext.access_time:
                    cached = None
                    cache_info = cache_ext
            if cache_info.etag != cache_ext.etag:
                cached = None
                cache_info = cache_ext
        if cached:
            # Using cached
            return Response(cached, cache_info)
        # Not using cached

        if not self.session:
            self._browser_init()

        if self.cache:
            headers = self.cache.prepare_headers(headers, cache_info)

        response = self._get(
            url,
            timeout=timeout,
            headers=headers,
            params=params
        )
        if "etag" in response.headers:
            if not cache_info:
                cache_info = CacheInfo()
            cache_info.etag = response.headers.get('etag')

        res = Response(cache_info=cache_info)

        if response.history:
            # list of responses in redirects
            code = 0

            for resp in response.history + [None]:
                if resp is None:
                    resp = response
                if code in [
                    requests.codes.FOUND,
                    requests.codes.SEE_OTHER,
                    requests.codes.TEMPORARY_REDIRECT
                ]:
                    self.info("Temporary redirect to {}".format(resp.url))
                elif code in [
                    requests.codes.MOVED_PERMANENTLY,
                    requests.codes.PERMANENT_REDIRECT
                ]:
                    self.warning("Moved to {}".format(resp.url))
                elif code != 0:
                    self.error("Code {} to {}".format(code, resp.url))
                code = resp.status_code

        if response.status_code == requests.codes.NOT_MODIFIED:
            self.info("Not modified {}".format(url))
            res.html, _ = self.cache.get(url, ignore_access_time=True)
            if self.cache:
                self.cache.update(url, cache_info)
            return res

        try:
            response.raise_for_status()
        except HTTPError as e:
            raise WEBConnectException("{} - {}".format(e, url))

        try:
            raw = response.content
            html = response.text
            if raw is None:
                self.warning("Response returned None")
                raise Exception()
            if html is None:
                self.warning("Response parsed returned None")
                raise Exception()
        except Exception:
            raise WEBConnectException("Unable to load {}".format(url))

        # TODO: cache raw / whole response object
        if self.cache:
            self.cache.put(url, html, cache_info)
        if url != response.url:
            if not response.history:
                self.warning(
                    "Response url different despite no redirects "
                    "{} - {}".format(url, response.url)
                )
            if self.cache:
                self.cache.put(response.url, html, cache_info)
        res.html = html
        res.raw = raw
        return res

    def _get_tag_match(self, ele, tree):
        """
        Match tag

        :param ele:
        :type ele:
        :param tree:
        :type tree: None, list
        :return:
        :rtype: None | list
        """
        if tree in [None, []]:
            return [ele]

        res = []
        t = tree[0]
        branch = tree[1:]
        attributes = {}

        for attr in t:
            if isinstance(t[attr], dict):
                if t[attr].get("type", None) == "reg":
                    t[attr] = re.compile(t[attr]['reg'])

        attributes.update(t)

        if "name" in attributes:
            del attributes['name']
        if "text" in attributes:
            del attributes['text']
        if "recursive" in attributes:
            del attributes['recursive']
        if "[]" in attributes:
            del attributes['[]']

        possibles = ele.find_all(
            t.get('name', None),
            text=t.get('text', None),
            attrs=attributes,
            recursive=t.get('recursive', True)
        )

        if not possibles:
            return None
        else:
            pass

        if "[]" in t:
            try:
                possibles = eval("possibles[{}]".format(t["[]"]))
            except:
                # no possibles
                return None

        if not isinstance(possibles, list):
            possibles = [possibles]

        for a in possibles:
            match = self._get_tag_match(a, branch)

            if match:
                res.extend(match)

        if not res:
            return None
        else:
            return res

    def _parse_value(self, eles, value_scheme):
        """

        :param eles:
        :type eles: list
        :param value_scheme:
        :type value_scheme: dict
        :return:
        :rtype: list
        """
        val = []
        val_type = value_scheme.get('type', None)
        reg = value_scheme.get('reg', None)
        strip = value_scheme.get('strip', False)

        for match in eles:
            if val_type == "text":
                val.append(unicode(match.getText()))
            elif val_type == "content":
                val.append(unicode(match.getText()))
            elif val_type == "attribute" and value_scheme.get("attribute", None):
                attr = value_scheme['attribute']

                if attr in match.attrs:
                    res = match[attr]

                    # multi-valued attributes will be joined in one string
                    if isinstance(res, list):
                        res = " ".join(res)
                    val.append(res)
            elif val_type == "html":
                val.append(unicode(match))
            else:
                # == html2text
                if self._text_maker is None:
                    val.append(html2text.html2text(unicode(match)))
                else:
                    val.append(self._text_maker.handle(unicode(match)))
            if strip:
                # TODO: github date field
                val[-1] = val[-1].strip()

        if reg:
            res = []

            for a in val:
                if isinstance(reg, dict):
                    if reg.get('type', None) == "reg":
                        reg = re.compile(reg['reg'])
                res.extend(reg.findall(a))
        else:
            res = val

        return res

    def _parse_scheme(self, ele, scheme):
        """

        :param ele:
        :type ele:
        :param scheme:
        :type scheme: dict[str |unicode, dict]
        :return:
        :rtype: dict
        """
        res = {}

        for aKey in scheme:
            entity = scheme[aKey]
            val = []
            matches = []
            res[aKey] = []

            if "tree" in entity:
                matches = self._get_tag_match(ele, entity['tree'])

                if not matches:
                    matches = []
                else:
                    pass
            else:
                # matches = [ele]
                pass

            if not matches and "value" == aKey:
                val.extend(self._parse_value([ele], entity))
                res[aKey].extend(val)

            if "value" == aKey:
                for a in matches:
                    # TODO: sure it's ele and not a?
                    val.extend(self._parse_value([ele], entity))
            if "children" in entity:
                for a in matches:
                    obj = {}
                    if "value" == aKey:
                        obj['value'] = val
                    child = self._parse_scheme(a, entity['children'])

                    if child:
                        obj.update(child)
                    if obj:
                        res[aKey].append(obj)
        return res

    def scrap(self,
              url=None, scheme=None, timeout=None,
              html_parser=None, cache_ext=None
    ):
        """
        Scrap a url and parse the content according to scheme

        :param url: Url to parse (default: self._url)
        :type url: str
        :param scheme: Scheme to apply to html (default: self._scheme)
        :type scheme: dict
        :param timeout: Timeout for http operation (default: self._timout)
        :type timeout: float
        :param html_parser: What html parser to use (default: self._html_parser)
        :type html_parser: str | unicode
        :param cache_ext: External cache info
        :type cache_ext: floscraper.models.CacheInfo
        :return: Response data from url and parsed info
        :rtype: floscraper.models.Response
        :raises WEBConnectException: HTTP get failed
        :raises WEBParameterException: Missing scheme or url
        """
        if not url:
            url = self.url
        if not scheme:
            scheme = self.scheme
        if not timeout:
            timeout = self.timeout
        if not html_parser:
            html_parser = self.html_parser
        if not scheme:
            raise WEBParameterException("Missing scheme definition")
        if not url:
            raise WEBParameterException("Missing url definition")
        resp = self.get(url, timeout, cache_ext=cache_ext)
        soup = BeautifulSoup(resp.html, html_parser)
        resp.scraped = self._parse_scheme(soup, scheme)
        return resp

    def _shrink_list(self, shrink):
        """
        Shrink list down to essentials

        :param shrink: List to shrink
        :type shrink: list
        :return: Shrunk list
        :rtype: list
        """
        res = []

        if len(shrink) == 1:
            return self.shrink(shrink[0])
        else:
            for a in shrink:
                temp = self.shrink(a)

                if temp:
                    res.append(temp)
        return res

    def _shrink_dict(self, shrink):
        """
        Shrink dict down to essentials

        :param shrink: Dict to shrink
        :type shrink: dict
        :return: Shrunk dict
        :rtype: dict
        """
        res = {}

        if len(shrink.keys()) == 1 and "value" in shrink:
            return self.shrink(shrink['value'])
        else:
            for a in shrink:
                res[a] = self.shrink(shrink[a])

                if not res[a]:
                    del res[a]
        return res

    def shrink(self, shrink):
        """
        Remove unnecessary parts

        :param shrink: Object to shringk
        :type shrink: dict | list
        :return: Shrunk object
        :rtype: dict | list
        """
        if isinstance(shrink, list):
            return self._shrink_list(shrink)
        if isinstance(shrink, dict):
            return self._shrink_dict(shrink)
        return shrink

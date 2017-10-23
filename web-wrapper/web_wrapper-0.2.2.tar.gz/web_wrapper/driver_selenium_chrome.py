import cutil
import logging
from selenium import webdriver
from web_wrapper.web import Web
from web_wrapper.selenium_utils import SeleniumUtils


logger = logging.getLogger(__name__)


class DriverSeleniumChrome(Web, SeleniumUtils):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver_type = 'selenium_chrome'
        self.opts = webdriver.ChromeOptions()
        self.update_headers(self.current_headers, update=False)
        self.set_proxy(self.current_proxy, update=False)
        self._create_session()

    # Headers Set/Get
    def set_headers(self, headers, update=True):
        logger.debug("Set chrome headers")

        self.current_headers = headers
        # TODO: Remove any headrs that are no longer in the dict

        # Clear headers?
        # TODO

        plugin_path = self._header_extension(add_or_modify_headers=self.current_headers)
        self.opts.add_extension(plugin_path)

        if update is True:
            # Recreate webdriver with new header
            self._update()

    def get_headers(self):
        # TODO: Try and get from chrome directly to be accurate
        return self.current_headers

    def update_headers(self, headers, update=True):
        self.current_headers.update(headers)
        self.set_headers(self.current_headers, update=True)

    def set_proxy(self, proxy, update=True):
        """
        Set proxy for chrome session
        """
        update_web_driver = False
        if self.current_proxy != proxy:
            # Did we change proxies?
            update_web_driver = True

        self.current_proxy = proxy
        if proxy is None:
            # TODO: Need to be able to remove a proxy if one is set
            pass
        else:
            proxy_parts = cutil.get_proxy_parts(proxy)

            if proxy_parts.get('user') is not None:
                # Proxy has auth, create extension to add to driver
                self.opts.add_extension(self._proxy_extension(proxy_parts))
            else:
                # Use the full proxy address passed in
                self.opts.add_argument('--proxy-server={}'.format(proxy))

        # Recreate webdriver with new proxy settings
        if update_web_driver is True:
            self._update()

    def _create_session(self):
        """
        Creates a fresh session with no/default headers and proxies
        """
        self.driver = webdriver.Chrome(chrome_options=self.opts, **self.driver_args)
        self.driver.set_window_size(1920, 1080)

    def _update(self):
        """
        Re create the web driver with the new proxy or header settings
        """
        logger.debug("Update chrome web driver")
        self.quit()
        self._create_session()

    def reset(self):
        """
        Kills old session and creates a new one with no proxies or headers
        """
        # Kill old connection
        self.quit()
        # Clear chrome configs
        self.opts = webdriver.ChromeOptions()
        # Create new web driver
        self._create_session()

    def quit(self):
        """
        Generic function to close distroy and session data
        """
        if self.driver is not None:
            self.driver.quit()
        self.driver = None

    ##
    # Chrome Utils
    ##
    def _proxy_extension(self, proxy_parts):
        """
        Creates a chrome extension for the proxy
        Only need to be done this way when using a proxy with auth
        """
        import zipfile
        manifest_json = """
                        {
                            "version": "1.0.0",
                            "manifest_version": 2,
                            "name": "Chrome Proxy",
                            "permissions": [
                                "proxy",
                                "tabs",
                                "unlimitedStorage",
                                "storage",
                                "<all_urls>",
                                "webRequest",
                                "webRequestBlocking"
                            ],
                            "background": {
                                "scripts": ["background.js"]
                            },
                            "minimum_chrome_version":"22.0.0"
                        }
                        """

        background_js = """
                        var config = {{
                                mode: "fixed_servers",
                                rules: {{
                                  singleProxy: {{
                                    scheme: "{schema}",
                                    host: "{host}",
                                    port: parseInt({port})
                                  }},
                                  bypassList: []
                                }}
                              }};

                        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

                        function callbackFn(details) {{
                            return {{
                                authCredentials: {{
                                    username: "{user}",
                                    password: "{password}"
                                }}
                            }};
                        }}

                        chrome.webRequest.onAuthRequired.addListener(
                                    callbackFn,
                                    {{urls: ["<all_urls>"]}},
                                    ['blocking']
                        );
                        """.format(**proxy_parts)

        plugin_file = 'proxy_auth_plugin.zip'
        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

        return plugin_file

    def _header_extension(self, remove_headers=[], add_or_modify_headers={}):
        """Create modheaders extension

        Source: https://vimmaniac.com/blog/bangal/modify-and-add-custom-headers-in-selenium-chrome-driver/

        kwargs:
            remove_headers (list): headers name to remove
            add_or_modify_headers (dict): ie. {"Header-Name": "Header Value"}

        return str -> plugin path
        """
        import string
        import zipfile

        plugin_file = 'custom_headers_plugin.zip'

        if remove_headers is None:
            remove_headers = []

        if add_or_modify_headers is None:
            add_or_modify_headers = {}

        if isinstance(remove_headers, list) is False:
            logger.error("remove_headers must be a list")
            return None

        if isinstance(add_or_modify_headers, dict) is False:
            logger.error("add_or_modify_headers must be dict")
            return None

        # only keeping the unique headers key in remove_headers list
        remove_headers = list(set(remove_headers))

        manifest_json = """
                        {
                            "version": "1.0.0",
                            "manifest_version": 2,
                            "name": "Chrome HeaderModV",
                            "permissions": [
                                "webRequest",
                                "tabs",
                                "unlimitedStorage",
                                "storage",
                                "<all_urls>",
                                "webRequestBlocking"
                            ],
                            "background": {
                                "scripts": ["background.js"]
                            },
                            "minimum_chrome_version":"22.0.0"
                        }
                        """

        background_js = string.Template("""
                                        function callbackFn(details) {
                                            var remove_headers = ${remove_headers};
                                            var add_or_modify_headers = ${add_or_modify_headers};

                                            function inarray(arr, obj) {
                                                return (arr.indexOf(obj) != -1);
                                            }

                                            // remove headers
                                            for (var i = 0; i < details.requestHeaders.length; ++i) {
                                                if (inarray(remove_headers, details.requestHeaders[i].name)) {
                                                    details.requestHeaders.splice(i, 1);
                                                    var index = remove_headers.indexOf(5);
                                                    remove_headers.splice(index, 1);
                                                }
                                                if (!remove_headers.length) break;
                                            }

                                            // modify headers
                                            for (var i = 0; i < details.requestHeaders.length; ++i) {
                                                if (add_or_modify_headers.hasOwnProperty(details.requestHeaders[i].name)) {
                                                    details.requestHeaders[i].value = add_or_modify_headers[details.requestHeaders[i].name];
                                                    delete add_or_modify_headers[details.requestHeaders[i].name];
                                                }
                                            }

                                            // add modify
                                            for (var prop in add_or_modify_headers) {
                                                details.requestHeaders.push(
                                                    {name: prop, value: add_or_modify_headers[prop]}
                                                );
                                            }

                                            return {requestHeaders: details.requestHeaders};
                                        }

                                        chrome.webRequest.onBeforeSendHeaders.addListener(
                                                    callbackFn,
                                                    {urls: ["<all_urls>"]},
                                                    ['blocking', 'requestHeaders']
                                        );
                                        """
                                        ).substitute(remove_headers=remove_headers,
                                                     add_or_modify_headers=add_or_modify_headers,
                                                     )

        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

        return plugin_file

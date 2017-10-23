import cutil
import logging
from selenium import webdriver
from web_wrapper.web import Web
from web_wrapper.selenium_utils import SeleniumUtils


logger = logging.getLogger(__name__)


class DriverSeleniumPhantomJS(Web, SeleniumUtils):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver_type = 'selenium_phantomjs'
        self.default_service_args = self.driver_args.get('service_args', [])
        self.driver_args['service_args'] = self.default_service_args
        self.dcap = dict(webdriver.DesiredCapabilities.PHANTOMJS)
        self.update_headers(self.current_headers, update=False)
        self.set_proxy(self.current_proxy, update=False)
        self._create_session()

    # Headers Set/Get
    def set_headers(self, headers, update=True):
        logger.debug("Set phantomjs headers")

        self.current_headers = headers

        # Clear headers
        self.dcap = dict(webdriver.DesiredCapabilities.PHANTOMJS)

        for key, value in headers.items():
            self.dcap['phantomjs.page.customHeaders.{}'.format(key)] = value

        if update is True:
            # Recreate webdriver with new header
            self._update()

    def get_headers(self):
        # TODO: Try and get from phantom directly to be accurate
        return self.current_headers

    def update_headers(self, headers, update=True):
        self.current_headers.update(headers)
        self.set_headers(self.current_headers, update=True)

    # Proxy Set/Get
    def set_proxy(self, proxy, update=True):
        """
        Set proxy for requests session
        """
        update_web_driver = False
        if self.current_proxy != proxy:
            # Did we change proxies?
            update_web_driver = True

        self.current_proxy = proxy
        if proxy is None:
            self.driver_args['service_args'] = self.default_service_args
        else:
            proxy_parts = cutil.get_proxy_parts(proxy)

            self.driver_args['service_args'].extend(['--proxy={host}:{port}'.format(**proxy_parts),
                                                     '--proxy-type={schema}'.format(**proxy_parts),
                                                     ])
            if proxy_parts.get('user') is not None:
                self.driver_args['service_args'].append('--proxy-auth={user}:{password}'.format(**proxy_parts))

        # Recreate webdriver with new proxy settings
        if update is True and update_web_driver is True:
            self._update()

    def get_proxy(self):
        return self.current_proxy

    # Session
    def _create_session(self):
        """
        Creates a fresh session with no/default headers and proxies
        """
        logger.debug("Create new phantomjs web driver")
        self.driver = webdriver.PhantomJS(desired_capabilities=self.dcap,
                                          **self.driver_args)
        self.driver.set_window_size(1920, 1080)

    def _update(self):
        """
        Re create the web driver with the new proxy or header settings
        """
        logger.debug("Update phantomjs web driver")
        self.quit()
        self._create_session()

    def reset(self):
        """
        Kills old session and creates a new one with no proxies or headers
        """
        # Kill old connection
        self.quit()
        # Clear proxy data
        self.driver_args['service_args'] = self.default_service_args
        # Clear headers
        self.dcap = dict(webdriver.DesiredCapabilities.PHANTOMJS)
        # Create new web driver
        self._create_session()

    def quit(self):
        """
        Generic function to close distroy and session data
        """
        if self.driver is not None:
            self.driver.quit()
        self.driver = None

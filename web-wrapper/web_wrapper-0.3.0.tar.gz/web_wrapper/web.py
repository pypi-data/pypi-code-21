import os
import sys
import time
import cutil
import urllib
import logging
import requests
from PIL import Image  # pip install pillow
from io import BytesIO
from bs4 import BeautifulSoup
from web_wrapper.selenium_utils import SeleniumHTTPError

logger = logging.getLogger(__name__)

"""
Things to add:
    - (selenium) Scroll to load page
    - (selenium) check if elem is on view and clickable
    - (requests) screenshot
"""


class Web:
    """
    Web related functions
    Need to be on its own that way each profile can have its own instance of it for proxy support
    """

    def __init__(self, headers={}, proxy=None, **driver_args):
        self.scraper = None

        self.driver = None
        self.driver_args = driver_args
        self.current_proxy = proxy

        # Number of times to re-try a url
        self._num_retries = 3

        if headers is not None:
            self.current_headers = headers
        else:
            self.current_headers = {}

        # Set the default response values
        self._reset_response()

    def _reset_response(self):
        """
        Vars to track per request made
        Run before ever get_site to clear previous values
        """
        self.status_code = None
        self.url = None
        self.response = None

    def get_image_dimension(self, url):
        """
        Return a tuple that contains (width, height)
        Pass in a url to an image and find out its size without loading the whole file
        If the image wxh could not be found, the tuple will contain `None` values
        """
        w_h = (None, None)
        try:
            if url.startswith('//'):
                url = 'http:' + url
            data = requests.get(url).content
            im = Image.open(BytesIO(data))

            w_h = im.size
        except Exception:
            logger.warning("Error getting image size {}".format(url), exc_info=True)

        return w_h

    def get_soup(self, raw_content, input_type='html'):
        rdata = None
        if input_type == 'html':
            rdata = BeautifulSoup(raw_content, 'html.parser')  # Other option: html5lib
        elif input_type == 'xml':
            rdata = BeautifulSoup(raw_content, 'lxml')
        return rdata

    def screenshot(self, save_path, element=None, delay=0):
        """
        This can be used no matter what driver that is being used
        * ^ Soon requests support will be added

        Save screenshot to local dir with uuid as filename
        then move the file to `filename` (path must be part of the file name)

        Return the filepath of the image
        """
        if save_path is None:
            logger.error("save_path cannot be None")
            return None

        save_location = cutil.norm_path(save_path)
        cutil.create_path(save_location)
        logger.info("Taking screenshot: {filename}".format(filename=save_location))

        if not self.driver_type.startswith('selenium'):
            logger.debug("Create tmp phantomjs web driver for screenshot")
            # Create a tmp phantom driver to take the screenshot for us
            from web_wrapper import DriverSeleniumPhantomJS
            headers = self.get_headers()  # Get headers to pass to the driver
            proxy = self.get_proxy()  # Get the current proxy being used if any
            # TODO: ^ Do the same thing for cookies
            screenshot_web = DriverSeleniumPhantomJS(headers=headers, proxy=proxy)
            screenshot_web.get_site(self.url, page_format='raw')
            screenshot_driver = screenshot_web.driver
        else:
            screenshot_driver = self.driver

        # If a background color does need to be set
        # self.driver.execute_script('document.body.style.background = "{}"'.format('white'))

        # Take screenshot
        # Give the page some extra time to load
        time.sleep(delay)
        if self.driver_type == 'selenium_chrome':
            # Need to do this for chrome to get a fullpage screenshot
            self.chrome_fullpage_screenshot(save_location, delay)
        else:
            screenshot_driver.get_screenshot_as_file(save_location)

        # Use .png extenstion for users save file
        if not save_location.endswith('.png'):
            save_location += '.png'

        # If an element was passed, just get that element so crop the screenshot
        if element is not None:
            logger.debug("Crop screenshot")
            # Crop the image
            el_location = element.location
            el_size = element.size
            try:
                cutil.crop_image(save_location,
                                 output_file=save_location,
                                 width=int(el_size['width']),
                                 height=int(el_size['height']),
                                 x=int(el_location['x']),
                                 y=int(el_location['y']),
                                 )
            except Exception as e:
                raise e.with_traceback(sys.exc_info()[2])

        if not self.driver_type.startswith('selenium'):
            # Quit the tmp driver created to take the screenshot
            screenshot_web.quit()

        return save_location

    def new_proxy(self):
        raise NotImplementedError

    def new_headers(self):
        raise NotImplementedError

    def _try_new_proxy(self):
        try:
            new_proxy = self.new_proxy()
            self.set_proxy(new_proxy)
        except NotImplementedError:
            logger.warning("No function new_proxy() found, not changing proxy")
        except Exception:
            logger.exception("Something went wrong when getting a new proxy")

    def _try_new_headers(self):
        try:
            new_headers = self.new_headers()
            self.set_headers(new_headers)
        except NotImplementedError:
            logger.warning("No function new_headers() found, not changing headers")
        except Exception:
            logger.exception("Something went wrong when getting a new header")

    def new_profile(self):
        logger.info("Create a new profile to use")
        self._try_new_proxy()
        self._try_new_headers()

    ###########################################################################
    # Get/load page
    ###########################################################################
    def get_site(self, url, cookies={}, page_format='html', return_on_error=[], retry_enabled=True,
                 num_tries=0, num_apikey_tries=0, headers={}, api=False, track_stat=True, timeout=30,
                 force_requests=False, driver_args=(), driver_kwargs={}):
        """
        headers & cookies - Will update to the current headers/cookies and just be for this request
        driver_args & driver_kwargs - Gets passed and expanded out to the driver
        """
        self._reset_response()

        num_tries += 1
        # Save args and kwargs so they can be used for trying the function again
        tmp_args = locals().copy()
        get_site_args = [tmp_args['url']]
        # Remove keys that dont belong to the keywords passed in
        del tmp_args['url']
        del tmp_args['self']
        get_site_kwargs = tmp_args

        # Check driver_kwargs for anything that we already set
        kwargs_cannot_be = ['headers', 'cookies', 'timeout']
        for key_name in kwargs_cannot_be:
            if driver_kwargs.get(key_name) is not None:
                del driver_kwargs[key_name]
                logger.warning("Cannot pass `{key}` in driver_kwargs to get_site(). `{key}` is already set by default"
                               .format(key=key_name))

        # Check if a url is being passed in
        if url is None:
            logger.error("Url cannot be None")
            return None

        ##
        # url must start with http....
        ##
        prepend = ''
        if url.startswith('//'):
            prepend = 'http:'

        elif not url.startswith('http'):
            prepend = 'http://'

        url = prepend + url

        ##
        # Try and get the page
        ##
        rdata = None
        try:
            rdata = self._get_site(url, page_format, headers, cookies, timeout, driver_args, driver_kwargs)

        ##
        # Exceptions from Selenium
        ##
        # Nothing yet

        ##
        # Exceptions from Requests
        ##
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            """
            Try again with a new profile (do not get new apikey)
            Wait n seconds before trying again
            """
            e_name = type(e).__name__
            if num_tries < self._num_retries and retry_enabled is True:
                logger.info("{} [get_site]: try #{} on {} Error {}".format(e_name, num_tries, url, e))
                time.sleep(2)
                self.new_profile()
                return self.get_site(*get_site_args, **get_site_kwargs)

            else:
                logger.error("{} [get_site]: try #{} on{}".format(e_name, num_tries, url))

        except requests.exceptions.TooManyRedirects as e:
            logger.exception("TooManyRedirects [get_site]: {}".format(url))

        ##
        # Exceptions shared by Selenium and Requests
        ##
        except (requests.exceptions.HTTPError, SeleniumHTTPError) as e:
            """
            Check the status code returned to see what should be done
            """
            status_code = str(e.response.status_code)
            # If the client wants to handle the error send it to them
            if int(status_code) in return_on_error:
                raise e.with_traceback(sys.exc_info()[2])

            try_again = self._get_site_status_code(url, status_code, api, num_tries, num_apikey_tries)
            if try_again is True and retry_enabled is True:
                # If True then try request again
                return self.get_site(*get_site_args, **get_site_kwargs)

        # Every other exceptions that were not caught
        except Exception:
            logger.exception("Unknown Exception [get_site]: {url}".format(url=url))

        return rdata

    def _get_site_status_code(self, url, status_code, api, num_tries, num_apikey_tries):
        """
        Check the http status code and num_tries/num_apikey_tries to see if it should try again or not
        Log any data as needed
        """
        # Make status code an int
        try:
            status_code = int(status_code)
        except ValueError:
            logger.exception("Incorrect status code passed in")
            return None
        # TODO: Try with the same api key 3 times, then try with with a new apikey the same way for 3 times as well
        # try_profile_again = False
        # if api is True and num_apikey_tries < self._num_retries:
        #     # Try with the same apikey/profile again after a short wait
        #     try_profile_again = True

        # Retry for any status code in the 400's or greater
        if status_code >= 400 and num_tries < self._num_retries:
            # Fail after 3 tries
            logger.info("HTTP {} error, try #{} on url: {}".format(status_code, num_tries, url))
            time.sleep(.5)
            self.new_profile()
            return True

        else:
            logger.warning("HTTPError [get_site]\n\t# of Tries: {}\n\tCode: {} - {}"
                           .format(num_tries, status_code, url))

        return None

    def download(self, url, save_path, header={}, redownload=False):
        """
        Currently does not use the proxied driver
        TODO: Be able to use cookies just like headers is used here
        :return: the path of the file that was saved
        """
        if save_path is None:
            logger.error("save_path cannot be None")
            return None

        # Get headers of current web driver
        header = self.get_headers()
        if len(header) > 0:
            # Add more headers if needed
            header.update(header)

        logger.debug("Download {url} to {save_path}".format(url=url, save_path=save_path))

        save_location = cutil.norm_path(save_path)
        if redownload is False:
            # See if we already have the file
            if os.path.isfile(save_location):
                logger.debug("File {save_location} already exists".format(save_location=save_location))
                return save_location

        # Create the dir path on disk
        cutil.create_path(save_location)

        if url.startswith('//'):
            url = "http:" + url
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=header)) as response,\
            open(save_location, 'wb') as out_file:
                data = response.read()
                out_file.write(data)

        except urllib.error.HTTPError as e:
            save_location = None
            # We do not need to show the user 404 errors
            if e.code != 404:
                logger.exception("Download Http Error {url}".format(url=url))

        except Exception:
            save_location = None
            logger.exception("Download Error: {url}".format(url=url))

        return save_location

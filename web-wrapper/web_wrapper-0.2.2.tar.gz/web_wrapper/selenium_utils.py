import os
import sys
import time
import json
import logging
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException


logger = logging.getLogger(__name__)


class SeleniumHTTPError(IOError):
    """
    An HTTP error occurred in Selenium
    Mimic requests.exceptions.HTTPError for status_code
    """

    def __init__(self, *args, **kwargs):
        self.response = type('', (), {})()

        # Match how the status code is formatted in requests.exceptions.HTTPError
        self.response.status_code = kwargs.get('status_code')


class SeleniumUtils:

    def get_selenium_header(self):
        """
        Return server response headers from selenium request
        Also includes the keys `status-code` and `status-text`
        """
        javascript = """
                     function parseResponseHeaders( headerStr ){
                       var headers = {};
                       if( !headerStr ){
                         return headers;
                       }
                       var headerPairs = headerStr.split('\\u000d\\u000a');
                       for( var i = 0; i < headerPairs.length; i++ ){
                         var headerPair = headerPairs[i];
                         var index = headerPair.indexOf('\\u003a\\u0020');
                         if( index > 0 ){
                           var key = headerPair.substring(0, index);
                           var val = headerPair.substring(index + 2);
                           headers[key] = val;
                         }
                       }
                       return headers;
                     }
                     var req = new XMLHttpRequest();
                     req.open('GET', document.location, false);
                     req.send(null);
                     var header = parseResponseHeaders(req.getAllResponseHeaders().toLowerCase());
                     header['status-code'] = req.status;
                     header['status-text'] = req.statusText;
                     return header;
                     """

        return self.driver.execute_script(javascript)

    def _get_site(self, url, page_format, headers, cookies, timeout, driver_args, driver_kwargs):
        """
        Try and return page content in the requested format using selenium
        """
        try:
            # **TODO**: Find what exception this will throw and catch it and call
            #   self.driver.execute_script("window.stop()")
            # Then still try and get the source from the page
            self.driver.set_page_load_timeout(timeout)

            self.driver.get(url)
            header_data = self.get_selenium_header()
            status_code = header_data['status-code']

            # Set data to access from script
            self.status_code = status_code
            self.url = self.driver.current_url

        except TimeoutException:
            logger.warning("Page timeout: {}".format(url))
            try:
                scraper_monitor.failed_url(url, 'Timeout')
            except (NameError, AttributeError):
                # Happens when scraper_monitor is not being used/setup
                pass
            except Exception:
                logger.exception("Unknown problem with scraper_monitor sending a failed url")

        except Exception as e:
            raise e.with_traceback(sys.exc_info()[2])

        else:
            # If an exception was not thrown then check the http status code
            if status_code < 400:
                # If the http status code is not an error
                rdata = None
                if page_format == 'html':
                    logger.debug("Convert selenium html into soup")
                    rdata = self.get_soup(self.driver.page_source, input_type='html')

                elif page_format == 'json':
                    logger.debug("Convert selenium json response into dict")
                    rdata = json.loads(self.driver.find_element_by_tag_name('body').text)

                elif page_format == 'xml':
                    logger.debug("Convert selenium xml response into soup")
                    rdata = self.get_soup(self.driver.page_source, input_type='xml')

                elif page_format == 'raw':
                    logger.debug("Do not convert the selenium response, return the page source as a string")
                    # Return unparsed html
                    # In this case just use selenium's built in find/parsing
                    rdata = self.driver.page_source

                else:
                    rdata = None

                return rdata
            else:
                # If http status code is 400 or greater
                raise SeleniumHTTPError("Status code >= 400", status_code=status_code)

    def hover(self, element):
        """
        In selenium, move cursor over an element
        :element: Object found using driver.find_...("element_class/id/etc")
        """
        javascript = """var evObj = document.createEvent('MouseEvents');
                        evObj.initMouseEvent(\"mouseover\", true, false, window, 0, 0, 0, 0, 0, \
                        false, false, false, false, 0, null);
                        arguments[0].dispatchEvent(evObj);"""

        if self.driver.selenium is not None:
            self.driver.selenium.execute_script(javascript, element)

    def reload_page(self):
        logger.info("Refreshing page...")
        if self.driver.selenium is not None:
            try:
                # Stop the current loading action before refreshing
                self.driver.selenium.send_keys(webdriver.common.keys.Keys.ESCAPE)
                self.driver.selenium.refresh()
            except Exception:
                logger.exception("Exception when reloading the page")

    def scroll_to_bottom(self):
        """
        Scoll to the very bottom of the page
        TODO: add increment & delay options to scoll slowly down the whole page to let each section load in
        """
        if self.driver.selenium is not None:
            try:
                self.driver.selenium.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            except WebDriverException:
                self.driver.selenium.execute_script("window.scrollTo(0, 50000);")
            except Exception:
                logger.exception("Unknown error scrolling page")

    def chrome_fullpage_screenshot(self, file, delay=0):
        """
        Fullscreen workaround for chrome
        Source: http://seleniumpythonqa.blogspot.com/2015/08/generate-full-page-screenshot-in-chrome.html
        """
        total_width = self.driver.execute_script("return document.body.offsetWidth")
        total_height = self.driver.execute_script("return document.body.parentNode.scrollHeight")
        viewport_width = self.driver.execute_script("return document.body.clientWidth")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        logger.info("Starting chrome full page screenshot workaround. Total: ({0}, {1}), Viewport: ({2},{3})"
                    .format(total_width, total_height, viewport_width, viewport_height))
        rectangles = []

        i = 0
        while i < total_height:
            ii = 0
            top_height = i + viewport_height

            if top_height > total_height:
                top_height = total_height

            while ii < total_width:
                top_width = ii + viewport_width

                if top_width > total_width:
                    top_width = total_width

                logger.debug("Appending rectangle ({0},{1},{2},{3})".format(ii, i, top_width, top_height))
                rectangles.append((ii, i, top_width, top_height))

                ii = ii + viewport_width

            i = i + viewport_height

        stitched_image = Image.new('RGB', (total_width, total_height))
        previous = None
        part = 0

        for rectangle in rectangles:
            if previous is not None:
                self.driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
                logger.debug("Scrolled To ({0},{1})".format(rectangle[0], rectangle[1]))
                time.sleep(delay)

            file_name = "part_{0}.png".format(part)
            logger.debug("Capturing {0} ...".format(file_name))

            self.driver.get_screenshot_as_file(file_name)
            screenshot = Image.open(file_name)

            if rectangle[1] + viewport_height > total_height:
                offset = (rectangle[0], total_height - viewport_height)
            else:
                offset = (rectangle[0], rectangle[1])

            logger.debug("Adding to stitched image with offset ({0}, {1})".format(offset[0], offset[1]))
            stitched_image.paste(screenshot, offset)

            del screenshot
            os.remove(file_name)
            part = part + 1
            previous = rectangle

        stitched_image.save(file)
        logger.info("Finishing chrome full page screenshot workaround...")
        return True

#!/usr/bin/env python3
"""tiny framework for parsing web.

This module provides base class for webparser, it can
    1. open webpages with selenium webdriver;
    2. run a set of parsers;
    3. handle selenium exceptions;
    4. log success and log fail.


Important
    To use a remote webdriver don't forget to start selenium server.
    $ java -jar selenium-server-standalone.jar


Example
        Create module contains parsers:
        #-------[ amazon.py ]---------------------------------------------------
            from webparser.crawler import Crawler

            class AmazonBook(Crawler):
                def __init__(self, url=None):
                    self.parsers = {self.parse_title, self.parse_cover_url}
                    super().__init__(url)

                def parse_title(self):
                    title = self.webdriver.find_element_by_xpath(
                        "//span[@id='productTitle'][1]"
                    ).get_attribute('innerHTML')
                    self.data['title'] = title
                    if title:
                        return None
                    return 'Title not found.'

                def parse_cover_url(self):
                    cover_url = self.webdriver.find_element_by_xpath(
                        "//img[@id='imgBlkFront'][1]"
                    ).get_attribute('src')
                    self.data['cover_url'] = cover_url
                    if cover_url:
                        return None
                    return 'Cover url not found.'
        #-----------------------------------------------------------------------

        Example script 01:
        #-------[ parser.py ]---------------------------------------------------
            from webparser.amazon import AmazonBook

            amazon_book = AmazonBook('http://...')  # Load webpage and parse it
            print(amazon_book.data['title'])        # Print parsed book title
            print(amazon_book.data['cover_url'])    # Print parsed url title
        #-----------------------------------------------------------------------

        Example script 02:
        #-------[ parser.py ]---------------------------------------------------
            from webparser.amazon import AmazonBook

            amazon_book = AmazonBook()        # Create object
            amazon_book.get('http://...')     # Load webpage
            amazon book.parse_title()         # Parse book title
            print(amazon_book.data['title'])  # Print parsed book title
        #-----------------------------------------------------------------------


Guideline [webdriver]
    1. Change default webdriver for new objects
        Crawler.webdriver = None
        Crawler.webdriver_default
            = lambda : Crawler.init_webdriver_chrome_remote(ip, port)

    2. Change default webdriver for new objects of selected class
        AmazonBook.webdriver = None
        AmazonBook.webdriver_default
            = lambda : Crawler.init_webdriver_chrome_remote(ip, port)

    3. Change webdriver for selected object
        myobject.webdriver = Crawler.init_webdriver_chrome_remote(ip, port)


Guideline [child classes]
    1. Realization of parsers should be placed in child classes.
        See the example of child class in the Example section.

    1.1 Child class should have constructor
        def __init__(self, url=None):
            self.parsers = {self.parse_title}  # Set of routine parsers
            super().__init__(url)              # Parent class constructor

    1.2 Child class should have parsers
        def parse_title(self):          # Recommend to begin name with 'parser_'
            '''Parses book title.'''    # Docstring is important for logs
            title = self.webdriver.find_element_by_xpath(
                "//span[@id='productTitle'][1]"
            ).get_attribute('src')      # Recommend to retrieve data with xpath
            self.data['title'] = title  # Data should be stored in data[]
            if title:
                return None             # If success, return None
            return 'Title not found.'   # If failed, return error message

    2. Recommend to make separate class for each webpage type,
        and separate module (with several classes) for each website.
        Example: module "amazon.py" with classes "AmazonBook", "AmazonCoupons".


Guideline [logging]
    1. Level WARNINGS:
        a) logs fail messages.

    2. Level INFO:
        a) logs exception messages about fails;
        b) logs success messages.

    3. Set log level in your script:
        import logging
        logging.basicConfig(level=logging.INFO)



Copyright (c) 2017 Mikhail Ananyevskiy

    This programm is free software; you can redistribute it and/or modify
    it under the terms of

                              MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""

# TODO:
# 1. Add webdrivers:
#    1.1 Add Opera
#    1.2 Add Firefox
#    1.3 Add Chrome


import logging
import selenium.webdriver
import selenium.common.exceptions


__version__ = r'1.00'
__author__ = r'Mikhail Ananyevskiy (aka soomrack) <soomrack@gmail.com>'
__date__ = r'05 October 2017'


class Crawler(object):
    """Base class for web webparser.

    Any webcrawler should be a child class of current class
    with realized routines for data retrieval (parsers).
    See current module docs for examples.

    Class attributes:
        webdriver: selenium.webdriver object.
            It is used by all new objects of current class or of child classes
            to interact with webpages (download, parse, etc.).
            This attribute can be overrided in a child class or in objects.

        parsers: empty set of functions (set of parsers).
            This attribute should be overrided in objects.
            and can be overrided in child class.

    Object attributes:
        data: dictionary.
            All data retrieved from webpage should be stored here.

        webpage: dictionary.
            All technical data about current webpage should be stored here,
            self.webpage['url'] is the url of current webpage.

    Optional object attributes (by default -- no exists):
        webdriver: selenium webdriver object.
            If exists, then object will interact with webpage
            through self.webdriver, ignoring cls.webdriver.

        parsers: set of functions (set of parsers).
            This attribute should be overrided in objects.
    """

    webdriver = None
    parsers = {}

    def __init__(self, url=None, parsers=None):
        """Inits object with webpage url and with the specified set of parsers.

        Args:
            url: string.
                Optional, if it is not None, then the initialization includes
                loading webpage, parsing it and closing it.
                Default value is None.

            parsers: set of functions.
                Optional, if it is not None, then object will use this set
                of functions as webpage parsers.
                Default value is None.
        """
        self.data = {}
        self.webpage = {}
        self.init_webdriver()
        if url:
            self.get_parse_close(url, parsers)

    @classmethod
    def init_webdriver(cls):
        """Inits webdriver (class attribute).

        Default webdriver depends on selected class, so this is a class method.
        """
        if not cls.webdriver:
            cls.webdriver = cls.webdriver_default()

    def get(self, url):
        """Try to open webpage in browser (i.e. selenium webdriver).

        New webpage means that self.data and self.webpage should be new,
        this way current routine erases self.data and self.webpage,
        then sets self.webpage['url'] to url.

        Args:
            url: string.

        Returns:
            True if download success, False otherwise.
        """
        self.data = {}
        self.webpage = {'url': url}
        try:
            self.webdriver.get(url)
            logging.info('[OK] get webpage {}'.format(url))
            return True
        except (selenium.common.exceptions.WebDriverException,
                AttributeError) as error:
            logging.warning('[FAIL] get webpage {}'.format(url))
            logging.info(error)
            return False

    def parse(self, parsers=None):
        """Run parser routines for object.

        This method is a routine for running parsers and handling exceptions.
        Each parser function should return None if success and error message
        if shit happens. The first line of parser docstring is logging with
        the status of the result (OK or FAIL).

        Args:
            parsers: set of functions (parsers).
                If parsers argument is None, then self.parsers set is used.

        Returns:
            Integer -- number of failed parsers.
            Returns 0 if all parsers were completed without errors.
        """
        errors_count = 0
        if not parsers:
            parsers = self.parsers
        for parser in parsers:
            parser_info = parser.__doc__.splitlines()[0]
            try:
                error_message = parser()
                if error_message:
                    logging.warning('[FAIL] {}'.format(parser_info))
                    logging.info(error_message)
                    errors_count += 1
                else:
                    logging.info('[OK] {}'.format(parser_info))
            except (selenium.common.exceptions.WebDriverException,
                    AttributeError) as error:
                logging.warning('[FAIL] {}'.format(parser_info))
                logging.info(error)
                errors_count += 1
        return errors_count

    def close(self):
        """Close webpage.

        This function may be useful if you don't want to keep connection
        to website. If you don't need webpage it is a good practice
        to close it in browser (i.e. in selenium webdriver).

        Returns:
            True is success, False otherwise.
        """
        try:
            self.webdriver.close()
            logging.info('[OK] close webpage.')
            return True
        except (selenium.common.exceptions.WebDriverException,
                AttributeError) as error:
            logging.warning('[FAIL] close webpage.')
            logging.info(error)
            return False

    def get_parse_close(self, url, parsers=None):
        """Composite function, runs self.get(), self.parse(), self.close().

        This method implements abstract algorithm
            Step 1. open webpage in browser;
            Step 2. retrieve data from webpage (parse it);
            Step 3. close webpage in browser.

        Args:
            url: string.
                See description of get() method.

            parsers: set of functions (parsers).
                See description of parse() method.

        Returns:
            True if success, False otherwise.
        """
        if self.get(url):
            is_parse_error = self.parse(parsers)
            is_close_error = self.close()
            return bool(is_parse_error and is_close_error)
        else:
            return False

    @staticmethod
    def webdriver_default():
        """Initializes the default webdriver.

        Replace this method to change the default webdriver, example:
            MyClass.webdriver_default = lambda :
                webparser.webdriver_chrome_remote_headless('127.0.0.1', '4444')

        By default webdriver initializes as
            webparser.webdriver_chrome_remote_headless('127.0.0.1', '4444')

        Returns:
            Selenium webdriver object.
        """
        return Crawler.webdriver_chrome_remote_headless('127.0.0.1', '4444')

    @staticmethod
    def webdriver_chrome_remote(ip_addr, port):
        """Initializes Chrome remote selenium webdriver.

        Args:
            ip_addr: string.
                Remote ip, example '127.0.0.1'.

            port: string.
                Remote port, example '4444'.

        Returns:
            Selenium webdriver object.
        """
        try:
            chrome_options = selenium.webdriver.ChromeOptions()
            webdriver = selenium.webdriver.Remote(
                command_executor='http://{}:{}/wd/hub'.format(ip_addr, port),
                desired_capabilities=chrome_options.to_capabilities()
            )
            logging.info('[OK] init Chrome remote.')
            return webdriver
        except (selenium.common.exceptions.WebDriverException,
                AttributeError) as error:
            logging.warning('[FAIL] init Chrome remote.')
            logging.info(error)
            return None

    @staticmethod
    def webdriver_chrome_remote_nojs(ip_addr, port):
        """Initializes Chrome remote selenium webdriver with no javascript.

        Args:
            ip_addr: string.
                Remote ip, example '127.0.0.1'.

            port: string.
                Remote port, example '4444'.

        Returns:
            Selenium webdriver object.
        """
        try:
            chrome_options = selenium.webdriver.ChromeOptions()
            chrome_options.add_argument('--disable-javascript')
            webdriver = selenium.webdriver.Remote(
                command_executor='http://{}:{}/wd/hub'.format(ip_addr, port),
                desired_capabilities=chrome_options.to_capabilities()
            )
            logging.info('[OK] init Chrome remote.')
            return webdriver
        except (selenium.common.exceptions.WebDriverException,
                AttributeError) as error:
            logging.warning('[FAIL] init Chrome remote.')
            logging.info(error)
            return None

    @staticmethod
    def webdriver_chrome_remote_headless(ip_addr, port):
        """Initializes Chrome remote headless selenium webdriver.

        Args:
            ip_addr: string.
                Remote ip, example '127.0.0.1'.

            port: string.
                Remote port, example '4444'.

        Returns:
            Selenium webdriver object.
        """
        try:
            chrome_options = selenium.webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            webdriver = selenium.webdriver.Remote(
                command_executor='http://{}:{}/wd/hub'.format(ip_addr, port),
                desired_capabilities=chrome_options.to_capabilities()
            )
            logging.info('[OK] init Chrome remote headless.')
            return webdriver
        except (selenium.common.exceptions.WebDriverException,
                AttributeError) as error:
            logging.warning('[FAIL] init Chrome remote headless.')
            logging.info(error)
            return None

    @staticmethod
    def webdriver_chrome_remote_headless_nojs(ip_addr, port):
        """Initializes Chrome remote headless selenium webdriver with no js.

        Args:
            ip_addr: string.
                Remote ip, example '127.0.0.1'.

            port: string.
                Remote port, example '4444'.

        Returns:
            Selenium webdriver object.
        """
        try:
            chrome_options = selenium.webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-javascript')
            webdriver = selenium.webdriver.Remote(
                command_executor='http://{}:{}/wd/hub'.format(ip_addr, port),
                desired_capabilities=chrome_options.to_capabilities()
            )
            logging.info('[OK] init Chrome remote headless.')
            return webdriver
        except (selenium.common.exceptions.WebDriverException,
                AttributeError) as error:
            logging.warning('[FAIL] init Chrome remote headless.')
            logging.info(error)
            return None


def main():
    """Print documentation and exit."""
    print(__doc__)


if __name__ == r'__main__':
    main()

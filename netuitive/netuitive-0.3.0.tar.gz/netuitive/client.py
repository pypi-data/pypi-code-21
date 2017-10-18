import logging
import json
import time

from netuitive import __version__

try:
    import urllib.request as urllib2
except ImportError:  # pragma: no cover
    import urllib2

try:
    from urllib.parse import urlparse
except ImportError:  # pragma: no cover
    from urlparse import urlparse


class Client(object):

    """
        Netuitive Rest Api Client for agent data ingest.
        Posts Element data to Netuitive Cloud

        :param url: Base data source URL
        :type url: string
        :param api_key: API Key for data source
        :type api_key: string


    """

    def __init__(self, url='https://api.app.netuitive.com/ingest',
                 api_key='apikey', agent='Netuitive-Python/' + __version__):

        if url.endswith('/'):
            url = url[:-1]

        self.url = url
        self.api_key = api_key
        self.dataurl = self.url + '/' + self.api_key
        self.timeurl = '{uri.scheme}://{uri.netloc}/time'.format(
            uri=urlparse(url))
        self.eventurl = self.dataurl.replace('/ingest/', '/ingest/events/', 1)
        self.checkurl = self.dataurl.replace('/ingest/', '/check/', 1) \
            .replace('/infrastructure', '', 1)
        self.agent = agent
        self.disabled = False
        self.kill_codes = [410, 418]
        self.post_error_count = 0
        self.max_post_errors = 10

    def post(self, element):
        """
            :param element: Element to post to Netuitive
            :type element: object
        """

        try:

            if self.disabled is True:
                element.clear_samples()
                logging.error('Posting has been disabled. '
                              'See previous errors for details.')
                return(False)

            if element.id is None:
                raise Exception('element id is not set')

            payload = json.dumps(
                [element], default=lambda o: o.__dict__, sort_keys=True)
            logging.debug(payload)

            headers = {'Content-Type': 'application/json',
                       'User-Agent': self.agent}
            request = urllib2.Request(
                self.dataurl, data=payload, headers=headers)
            resp = urllib2.urlopen(request)
            logging.debug("Response code: %d", resp.getcode())

            resp.close()

            self.post_error_count = 0

            return(True)

        except urllib2.HTTPError as e:
            logging.debug("Response code: %d", e.code)

            if e.code in self.kill_codes:
                self.disabled = True

                logging.exception('Posting has been disabled.'
                                  'See previous errors for details.')
            else:
                self.post_error_count += 1
                if self.post_error_count > self.max_post_errors:
                    element.clear_samples()

                logging.exception(
                    'error posting payload to api ingest endpoint (%s): %s',
                    self.dataurl, e)

        except Exception as e:
            self.post_error_count += 1
            if self.post_error_count > self.max_post_errors:
                element.clear_samples()  # pragma: no cover

            logging.exception(
                'error posting payload to api ingest endpoint (%s): %s',
                self.dataurl, e)

    def post_event(self, event):
        """
            :param event: Event to post to Netuitive
            :type event: object
        """

        if self.disabled is True:
            logging.error('Posting has been disabled. '
                          'See previous errors for details.')
            return(False)

        payload = json.dumps(
            [event], default=lambda o: o.__dict__, sort_keys=True)
        logging.debug(payload)
        try:
            headers = {'Content-Type': 'application/json',
                       'User-Agent': self.agent}
            request = urllib2.Request(
                self.eventurl, data=payload, headers=headers)
            resp = urllib2.urlopen(request)
            logging.debug("Response code: %d", resp.getcode())
            resp.close()

            return(True)

        except urllib2.HTTPError as e:
            logging.debug("Response code: %d", e.code)

            if e.code in self.kill_codes:
                self.disabled = True
                logging.exception('Posting has been disabled.'
                                  'See previous errors for details.')
            else:
                logging.exception(
                    'error posting payload to api ingest endpoint (%s): %s',
                    self.eventurl, e)

        except Exception as e:
            logging.exception(
                'error posting payload to api ingest endpoint (%s): %s',
                self.eventurl, e)

    def post_check(self, check):
        """
            :param check: Check to post to Metricly
            :type check: object
        """

        if self.disabled is True:
            logging.error('Posting has been disabled. '
                          'See previous errors for details.')
            return(False)

        url = self.checkurl + '/' \
            + check.name + '/' \
            + check.elementId + '/' \
            + str(check.interval)
        try:
            headers = {'User-Agent': self.agent}
            request = urllib2.Request(
                url, data='', headers=headers)
            resp = urllib2.urlopen(request)
            logging.debug("Response code: %d", resp.getcode())
            resp.close()

            return(True)

        except urllib2.HTTPError as e:
            logging.debug("Response code: %d", e.code)

            if e.code in self.kill_codes:
                self.disabled = True
                logging.exception('Posting has been disabled.'
                                  'See previous errors for details.')
            else:
                logging.exception(
                    'error posting payload to api ingest endpoint (%s): %s',
                    url, e)

        except Exception as e:
            logging.exception(
                'error posting payload to api ingest endpoint (%s): %s',
                url, e)

    def check_time_offset(self, epoch=None):
        req = urllib2.Request(self.timeurl,
                              headers={'User-Agent': self.agent})
        req.get_method = lambda: 'HEAD'
        resp = urllib2.urlopen(req)
        rdate = resp.info()['Date']

        if epoch is None:
            ltime = int(time.mktime(time.gmtime()))

        else:
            ltime = epoch

        rtime = int(time.mktime(
            time.strptime(rdate, "%a, %d %b %Y %H:%M:%S %Z")))

        ret = ltime - rtime

        return(ret)

    def time_insync(self):
        if self.check_time_offset() in range(-300, 300):
            return(True)

        else:
            return(False)

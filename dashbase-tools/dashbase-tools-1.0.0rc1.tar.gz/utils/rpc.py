from __future__ import print_function

import simplejson
import urllib3
from urllib3.util import Retry


class RPC(object):
    def __init__(self, host_port, num_tries=5, delay_in_sec=5):
        urllib3.disable_warnings()
        if host_port.startswith('http://') or host_port.startswith('https://'):
            self.url = host_port
        else:
            self.url = 'https://' + host_port
        self.num_tries = num_tries
        self.delay_in_sec = delay_in_sec
        self.headers = None
        self.conn = None
        self.init_connection()

    def init_connection(self):
        retries = Retry(connect=self.num_tries, backoff_factor=1)
        self.headers = {"Content-type": "text/plain", "Accept": "application/json"}
        self.conn = urllib3.connection_from_url(self.url, timeout=600, retries=retries, maxsize=5)

    def do_get(self, url):
        response = self.conn.request("GET", url)
        return response

    def do_post(self, url, data):
        data_string = simplejson.dumps(data)
        headers = {"Content-type": "application/json", "Accept": "application/json"}
        response = self.conn.urlopen("POST", url, body=data_string, timeout=600, headers=headers)
        return response

    def close(self):
        print("Connection closed.")
        self.conn.close()

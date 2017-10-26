from __future__ import absolute_import, unicode_literals

import sys
import socket
import json
from ilabs.client.get_user_key import get_user_key
from ilabs.client import __version__

try:
    from urllib2 import Request, urlopen
except ImportError:
    from urllib.request import Request, urlopen

def send_request(method, url, data=None, headers=None):
    assert method in ('GET', 'POST')
    if data is not None:
        assert method == 'POST'
    else:
        assert method == 'GET'

    # ugly!
    if sys.version_info[0] < 3:
        url = url.decode()

    return urlopen(Request(url, headers=headers, data=data))

def noop(*av, **kav): pass

_DEFAULT_USER_AGENT = 'ILabs API client ' + __version__


class ILabsApi:

    URL_API_BASE = 'https://api.innodatalabs.com/v1'

    URL_PING     = URL_API_BASE + '/ping'

    URL_INPUT    = URL_API_BASE + '/documents/input/'
    URL_OUTPUT   = URL_API_BASE + '/documents/output/'
    URL_FEEDBACK = URL_API_BASE + '/documents/training/{domain}/'

    URL_PREDICT  = URL_API_BASE + '/reference/{domain}/{name}'
    URL_STATUS   = URL_API_BASE + '/reference/{domain}/{task_id}/status'
    URL_CANCEL   = URL_API_BASE + '/reference/{domain}/{task_id}/cancel'

    def __init__(self, user_key=None, timeout=None, user_agent=None):
        self._user_key = user_key or get_user_key()
        if self._user_key is None:
            raise RuntimeError('Could not find credentials')
        self._user_agent = user_agent or _DEFAULT_USER_AGENT
        self._timeout = timeout
        if self._timeout is None:
            self._timeout = socket._GLOBAL_DEFAULT_TIMEOUT

    def _request(self, method, url, data=None, content_type=None):
        headers = {
            b'User-Key'     : self._user_key.encode(),
            b'User-Agent'   : self._user_agent.encode(),
            b'Cache-Control': b'no-cache'
        }
        if content_type is not None:
            headers[b'Content-Type'] = content_type.encode()
        res = send_request(method, url,
            data=data,
            headers= headers
        )

        if res.getcode() not in (200, 202):
            raise RuntimeError('REST endpoint returned error: %s' % res.getcode())

        return res.read()

    def _post(self, url, data, content_type=None):
        return self._request('POST', url, data, content_type=content_type)

    def get(self, url):
        '''
        Issues GET request with credentials.
        Useful for status/ and cancel/ REST operations using
        urls returned from predict() call.
        '''
        return self._request('GET', url)

    def ping(self):
        '''
        Checks that API is accessible.

        Always returns this: { "ping": "pong" }.
        '''
        out = self.get(self.URL_PING)
        return json.loads(out.decode())

    def upload_input(self, binary_data, filename=None):
        '''
        Upload file to the input cloud folder as "filename".
        If "filename" is None, system will generate name for you.

        The best practice is to let system auto-generate name for you.

        Returns dictionary with the following keys:

        - bytes_accepted  - number of bytes in the uploaded file
        - input_filename  - the name of the file
        '''
        url = self.URL_INPUT
        if filename:
            validate_filename(filename)
            url = self.URL_INPUT + filename
        out = self._post(url,
            data=binary_data,
            content_type='application/octet-stream')
        out = json.loads(out.decode())
        bytes_accepted = int(out['bytes_accepted'])
        if bytes_accepted != len(binary_data):
            raise RuntimeError('internal upload error: %r' % out)
        return out

    def download_input(self, filename):
        '''
        Downloads file from the input cloud folder.

        Returns binary contents of the file.
        '''
        validate_filename(filename)
        return self.get(self.URL_INPUT + filename)

    def predict(self, domain, filename):
        '''
        Schedules a task to run prediction on file "filename" using
        domain "domain".

        Returns dictionary with the following keys:

        - task_id   - task id
        - task_cancel_url  - use this url to cancel the task
        - document_output_url - use this url to download prediction result
        - tast_status_url - query status
        - output_filename - name of the output file (created only after task
            successfully completes)
        - version - ???
        '''
        validate_filename(filename)
        url = self.URL_PREDICT.format(
            domain=domain,
            name=filename)
        out = self.get(url)
        return json.loads(out.decode())

    def status(self, domain, task_id):
        '''Query status of a task sceduled with predict() method

        It is recommended that clients use pre-built URL string
        returned by predict() call in 'task_status_url' to query
        the task status, instead of using this method.

        Returns dictionary with the following keys:

        - error - [optional] if present, indicates task execution error
        - completed - true or false. Typically client polls API until it
            sees compleded==True. This field is always present.
        - progress - number indicating current step
        - steps - estimated total number of steps in this task
        - message - [optional] contains progress message
        '''

        url = self.URL_STATUS.format(
            domain=domain,
            task_id=task_id)
        out = self.get(url)
        return json.loads(out.decode())

    def cancel(self, domain, task_id):
        '''
        Cancel task scheduled with predict() method.

        It is recommended that clients use pre-built URL string
        returned by predict() call in 'task_cancel_url' to cancel
        the running task, instead of using this method.
        '''
        url = self.URL_CANCEL.format(
            domain=domain,
            task_id=task_id)
        out = self.get(url)
        return json.loads(out.decode())

    def download_output(self, filename):
        '''
        Retrieves file from output cloud folder

        It is recommended that clients use pre-built URL string
        returned by predict() call in 'document_output_url' to retrieve
        the prediction result, instead of using this method.
        '''
        validate_filename(filename)
        return self.get(self.URL_OUTPUT + filename)

    def upload_feedback(self, domain, filename, binary_data):
        '''
        Uploads file to training folder for the given "domain".
        Use it to provide prediction feedback like this:

        - send file for prediction
        - receive the prediction result
        - review predicted file and edit if necessary (to correct prediction mistakes)
        - upload to training folder using this method
        '''
        validate_domain(domain)
        validate_filename(filename)
        url = self.URL_FEEDBACK.format(domain=domain) + filename
        out = self._post(url,
            data=binary_data,
            content_type='application/octet-stream')
        out = json.loads(out.decode())

        if out['bytes_accepted'] != len(binary_data):
            raise RuntimeError('internal upload error: %r' % out)

        return out

def validate_domain(domain):
    if '/' in domain or '..' in domain:
        raise ValueError('domain can not contain slashes nor double dots: %r' % domain)

def validate_filename(filename):
    if '/' in filename or '..' in filename:
        raise ValueError('file name can not contain slashes nor double dots: %r' % domain)

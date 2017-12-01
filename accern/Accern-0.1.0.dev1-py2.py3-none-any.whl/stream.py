"""Python library for Accern Streaming API.

Core client functionality, common across all API requests (including performing
HTTP requests).
"""
from accern import error, util
from accern.util import six, urlsplit, urlunsplit, urlencode
import codecs
# from datetime import datetime

import re
import requests
# from requests.exceptions import Timeout
import sys
import time

api_base = "http://feed-staging.accern.com/v4/stream"
end_of_field = re.compile(r'\r\n\r\n|\r\r|\n\n')


class Event(object):

    sse_line_pattern = re.compile('(?P<name>[^:]*):?( ?(?P<value>.*))?')

    def __init__(self, data='', event='message', id=None, retry=None):
        self.data = data
        self.event = event
        self.id = id
        self.retry = retry

    def dump(self):
        lines = []
        if self.id:
            lines.append('id: %s' % self.id)

        # Only include an event line if it's not the default already.
        if self.event != 'message':
            lines.append('event: %s' % self.event)

        if self.retry:
            lines.append('retry: %s' % self.retry)

        lines.extend('data: %s' % d for d in self.data.split('\n'))
        return '\n'.join(lines) + '\n\n'

    @classmethod
    def parse(cls, raw):
        """Given a possibly-multiline string representing an SSE message, parse it and return a Event object."""
        msg = cls()
        for line in raw.splitlines():
            m = cls.sse_line_pattern.match(line)
            if m is None:
                # Malformed line.  Discard but warn.
                sys.stderr.write('Invalid SSE line: "%s"' % line, SyntaxWarning)
                continue

            name = m.group('name')
            if name == '':
                # line began with a ":", so is a comment.  Ignore
                continue
            value = m.group('value')

            if name == 'data':
                # If we already have some data, then join to it with a newline.
                # Else this is it.
                if msg.data:
                    msg.data = '%s\n%s' % (msg.data, value)
                else:
                    msg.data = value
            elif name == 'event':
                msg.event = value
            elif name == 'id':
                msg.id = value
            elif name == 'retry':
                msg.retry = int(value)

        return msg

    def __str__(self):
        return self.data


class StreamListener(object):
    def on_data(self, raw_data):
        """Call when raw data is received from connection.

        Override this method if you want to manually handle stream data. Return
        False to stop stream and close connection.
        """
        data = util.json.loads(raw_data)
        if 'disconnect' in data:
            if self.on_disconnect(data['disconnect']) is False:
                return False
        return raw_data

    def on_disconnect(self, notice):
        """Call when server return a disconnect notice."""
        return


class Stream(object):
    """Perform requests to the Accern API web services."""

    def __init__(self, listener, token, **kwargs):
        """Intialize with params.

        :param client: default http client. Optional
        :param token: Accern API token. Required.
        """
        self.api_base = api_base
        # Keep data here as it streams in
        self.buf = u''
        self.chunk_size = kwargs.get("chunk_size", 1024)
        self.last_id = kwargs.get("last_id", None)
        self._listener = listener
        self.new_session()
        # Any extra kwargs will be fed into the requests.get call later.
        self.requests_kwargs = kwargs
        self.retry_count = kwargs.get("retry_count", 3000)
        self.timeout = kwargs.get('timeout', 300.0)
        self.token = token

        # The SSE spec requires making requests with Cache-Control: nocache
        if 'headers' not in self.requests_kwargs:
            self.requests_kwargs['headers'] = {}
        self.requests_kwargs['headers']['Cache-Control'] = 'no-cache'

        # The 'Accept' header is not required, but explicit > implicit
        self.requests_kwargs['headers']['Accept'] = 'text/event-stream'

    def __iter__(self):
        return self

    def __next__(self):
        decoder = codecs.getincrementaldecoder(self.resp.encoding)(errors='replace')
        while not self._event_complete():
            try:
                next_chunk = next(self.resp_iterator)
                if not next_chunk:
                    raise EOFError()
                self.buf += decoder.decode(next_chunk)

            except (StopIteration, requests.RequestException, EOFError):
                time.sleep(self.retry / 1000.0)
                self._connect()

                # The SSE spec only supports resuming from a whole message, so
                # if we have half a message we should throw it out.
                head, sep, tail = self.buf.rpartition('\n')
                self.buf = head + sep
                continue

        # Split the complete event (up to the end_of_field) into event_string,
        # and retain anything after the current complete event in self.buf
        # for next time.
        (event_string, self.buf) = re.split(end_of_field, self.buf, maxsplit=1)
        msg = Event.parse(event_string)

        # If the server requests a specific retry delay, we need to honor it.
        if msg.retry:
            self.retry = msg.retry

        # last_id should only be set if included in the message.  It's not
        # forgotten if a message omits it.
        if msg.id:
            self.last_id = msg.id

        if msg.data:
            if self._listener.on_data(msg.data) is False:
                return False

        self.__next__()

    def _api_encode(self, data):
        for key, value in six.iteritems(data):
            key = util.utf8(key)
            if value is None:
                continue
            elif isinstance(value, list):
                yield (key, ",".join(value))
            else:
                yield (key, util.utf8(value))

    def _build_api_url(self, url, query):
        scheme, netloc, path, base_query, fragment = urlsplit(url)
        if base_query:
            query = '%s&%s' % (base_query, query)
        return urlunsplit((scheme, netloc, path, query, fragment))

    def _event_complete(self):
        return re.search(end_of_field, self.buf) is not None

    def _run(self):

        if self.last_id:
            self.requests_kwargs['headers']['Last-Event-ID'] = self.last_id
        # Use session if set.  Otherwise fall back to requests module.
        requester = self.session or requests
        self.resp = requester.get(self.url, stream=True)
        self.resp_iterator = self.resp.iter_content(chunk_size=self.chunk_size)

        # TODO(redirect): Ensure we're handling redirects.  Might also stick the 'origin'
        # attribute on Events like the Javascript spec requires.
        self.resp.raise_for_status()
        self.__next__()

    def new_session(self):
        self.session = requests.Session()
        self.session.params = None

    def performs(self):
        """Perform HTTP GET/POST with credentials.

        :param output: output config.

        :param params: HTTP GET parameters.

        :raises ApiError: when the API returns an error.
        :raises Timeout: if the request timed out.
        :raises TransportError: when something went wrong while trying to
            exceute a request.
        """
        if self.token:
            my_token = self.token
        else:
            from accern import token
            my_token = token

        if my_token is None:
            raise error.AuthenticationError('No Token provided')

        abs_url = '%s' % (self.api_base)
        params = self.requests_kwargs.get("params", None)
        if params is None:
            params = {'token': my_token}
        else:
            params['token'] = my_token
        encoded_params = urlencode(list(self._api_encode(params or {})))

        self.url = self._build_api_url(abs_url, encoded_params)

        self._run()

    if six.PY2:
        next = __next__

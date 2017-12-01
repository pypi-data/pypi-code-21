from accern import error
import codecs
import re
import six
import sys
import textwrap
import time


try:
    import requests
except ImportError:
    requests = None
else:
    try:
        # Require version 0.8.8, but don't want to depend on distutils
        version = requests.__version__
        major, minor, patch = [int(i) for i in version.split('.')]
    except Exception:
        # Probably some new-fangled version, so it should support verify
        pass
    else:
        if (major, minor, patch) < (0, 8, 8):
            sys.stderr.write(
                'Warning: the Accern library requires that your Python '
                '"requests" library be newer than version 0.8.8, but your '
                '"requests" library is version %s. Stripe will fall back to '
                'an alternate HTTP library so everything should work. We '
                'recommend upgrading your "requests" library. If you have any '
                'questions, please contact support@accern.com. (HINT: running '
                '"pip install -U requests" should upgrade your requests '
                'library to the latest version.)' % (version,))
            requests = None


__all__ = [
    'SSEClient',
    'new_default_http_client'
]


def new_default_http_client(*args, **kwargs):
    return RequestsClient(*args, **kwargs)


class HTTPClient(object):
    def request(self, method, url, headers, post_data=None):
        raise NotImplementedError(
            'HTTPClient subclasses must implement `request`')


class RequestsClient(HTTPClient):
    name = 'requests'

    def __init__(self, timeout=80, session=None, **kwargs):
        super(RequestsClient, self).__init__(**kwargs)
        self._timeout = timeout
        self._session = session or requests.Session()

    def request(self, method, url, headers, post_data=None):
        kwargs = {}
        try:
            try:
                result = self._session.request(method,
                                               url,
                                               headers=headers,
                                               data=post_data,
                                               timeout=self._timeout,
                                               **kwargs)
            except TypeError as e:
                raise TypeError(
                    'Warning: It looks like your installed version of the '
                    '"requests" library is not compatible with Stripe\'s '
                    'usage thereof. (HINT: The most likely cause is that '
                    'your "requests" library is out of date. You can fix '
                    'that by running "pip install -U requests".) The '
                    'underlying error was: %s' % (e,))
            content = result.content
            status_code = result.status_code
        except Exception as e:
            # Would catch just requests.exceptions.RequestException, but can
            # also raise ValueError, RuntimeError, etc.
            self._handle_request_error(e)
        return content, status_code, result.headers

    def _handle_request_error(self, e):
        if isinstance(e, requests.exceptions.RequestException):
            msg = ("Unexpected error communicating with Stripe.  "
                   "If this problem persists, let us know at "
                   "support@stripe.com.")
            err = "%s: %s" % (type(e).__name__, str(e))
        else:
            msg = ("Unexpected error communicating with Stripe. "
                   "It looks like there's probably a configuration "
                   "issue locally.  If this problem persists, let us "
                   "know at support@stripe.com.")
            err = "A %s was raised" % (type(e).__name__,)
            if str(e):
                err += " with error message %s" % (str(e),)
            else:
                err += " with no error message"
        msg = textwrap.fill(msg) + "\n\n(Network error: %s)" % (err,)
        raise error.APIConnectionError(msg)


end_of_field = re.compile(r'\r\n\r\n|\r\r|\n\n')


class SSEClient(object):
    def __init__(self, url, last_id=None, retry=3000, session=None, chunk_size=1024, **kwargs):
        self.url = url
        self.last_id = last_id
        self.retry = retry
        self.chunk_size = chunk_size

        # Optional support for passing in a requests.Session()
        self.session = session

        # Any extra kwargs will be fed into the requests.get call later.
        self.requests_kwargs = kwargs

        # The SSE spec requires making requests with Cache-Control: nocache
        if 'headers' not in self.requests_kwargs:
            self.requests_kwargs['headers'] = {}
        self.requests_kwargs['headers']['Cache-Control'] = 'no-cache'

        # The 'Accept' header is not required, but explicit > implicit
        self.requests_kwargs['headers']['Accept'] = 'text/event-stream'

        # Keep data here as it streams in
        self.buf = u''

        self._connect()

    def _connect(self):
        if self.last_id:
            self.requests_kwargs['headers']['Last-Event-ID'] = self.last_id

        # Use session if set.  Otherwise fall back to requests module.
        requester = self.session or requests
        self.resp = requester.get(self.url, stream=True, **self.requests_kwargs)
        self.resp_iterator = self.resp.iter_content(chunk_size=self.chunk_size)

        # TODO(redirect): Ensure we're handling redirects.  Might also stick the 'origin'
        # attribute on Events like the Javascript spec requires.
        self.resp.raise_for_status()

    def _event_complete(self):
        return re.search(end_of_field, self.buf) is not None

    def __iter__(self):
        return self

    def __next__(self):
        decoder = codecs.getincrementaldecoder(
            self.resp.encoding)(errors='replace')
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

        return msg

    if six.PY2:
        next = __next__


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

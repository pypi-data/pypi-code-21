import logging
import steov

class _NoopHouse:
    def persist (self, blob):
        import hashlib
        if blob is None:
            return None
        return hashlib.sha256(blob).hexdigest()

class RequestsWebGap:
    _noop_house = _NoopHouse()

    def __init__ (self, requests, session_factory=None, house=None, logger=None, censor={}):
        self._requests = requests
        self._session_factory = session_factory or self._requests.Session
        self._house = house or self._noop_house
        self._logger = logger or logging.getLogger(__name__)
        self._censor = set(map(str.casefold, censor))

    def _log_call_request (self, id, request, timeout):
        self._logger.debug("call.request.start: " + str(id))
        self._logger.debug("call.request.url: " + request.url)
        self._logger.debug("call.request.method: " + request.method)
        for k, v in request.headers.items():
            if k.casefold() in self._censor:
                v = "CENSORED"
            self._logger.debug("call.request.header." + k + ": " + v)
        self._logger.debug("call.request.body.sha256: " + str(self._house.persist(request.body)))
        self._logger.debug("call.request.timeout: " + str(None if timeout is None else timeout.total_seconds()))
        self._logger.debug("call.request.finish: " + str(id))

    def _log_call_error (self, id, exception, stacktrace):
        self._logger.debug("call.error.start: " + str(id))
        for k, v in getattr(exception, "__dict__", {}).items():
            self._logger.debug("call.error.exception." + k + ": " + repr(v))
        for line in stacktrace.splitlines(keepends=False):
            self._logger.debug("call.error.stacktrace.line: " + line)
        self._logger.debug("call.error.finish: " + str(id))

    def _log_call_response (self, id, response):
        self._logger.debug("call.response.start: " + str(id))
        self._logger.debug("call.response.status: " + str(response.status_code))
        self._logger.debug("call.response.message: " + response.reason)
        for k, v in response.headers.items():
            self._logger.debug("call.response.header." + k + ": " + v)
        self._logger.debug("call.response.body.sha256: " + str(self._house.persist(response.content)))
        self._logger.debug("call.response.elapsed: " + str(response.elapsed.total_seconds()))
        self._logger.debug("call.response.finish: " + str(id))

    def call (self, url, method="GET", headers={}, body=None, timeout=None, verify=True):
        import uuid
        call_id = uuid.uuid4()
        self._logger.debug("call.start: " + str(call_id))
        try:
            timeout_sec = None if timeout is None else timeout.total_seconds()
            request = self._requests.Request(url=url, method=method, headers=headers, data=body)
            with self._session_factory() as session:
                prepared_request = session.prepare_request(request)
                self._log_call_request(call_id, prepared_request, timeout)
                try:
                    response = session.send(prepared_request, timeout=timeout_sec, verify=verify)
                except Exception as ex:
                    # TODO sometimes `ex` can hold a response object. log it?
                    self._log_call_error(call_id, ex, steov.format_exc())
                    raise
                for i, historical_response in enumerate(list(response.history) + [response]):
                    if i > 0:
                        self._log_call_request(call_id, historical_response.request, timeout)
                    self._log_call_response(call_id, historical_response)
                return steov.Anon({
                    "status": response.status_code,
                    "message": response.reason,
                    "headers": dict(response.headers),
                    "body": response.content,
                    "_orig_response": response,
                })
        finally:
            self._logger.debug("call.finish: " + str(call_id))

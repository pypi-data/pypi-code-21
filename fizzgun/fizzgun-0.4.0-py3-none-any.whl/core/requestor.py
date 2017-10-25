
from fizzgun.models import HttpRequest
from fizzgun.application.service_contexts import RequestorContext
from fizzgun.core.common import Worker


class Requestor(Worker):
    """
    Perform HTTP requests (from mutated templates), includes the obtained response
    and sends it to the next node in the chain.
    """

    # Overrides
    def process(self, work):
        """Executes the mutated request and adds the obtained response"""
        response = self._do_request(work['modified'])
        work['response'] = self._convert(*response)
        yield work

    def _do_request(self, req):
        req = HttpRequest(req)
        return self.requestor_context.http_client.request(req.method, req.url, req.headers, req.body)

    @classmethod
    def _convert(cls, status, reason, headers, body):
        return {
            'status': status,
            'reason': reason,
            'headers': [(k, v) for k, v in headers.items()],
            'body': body
        }

    @property
    def requestor_context(self) -> RequestorContext:
        return self.service_context

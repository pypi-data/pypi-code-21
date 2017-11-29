import time

def dispatch(self, request, *args, **kwargs):
    """
    `.dispatch()` is pretty much the same as Django's regular dispatch,
    but with extra hooks for startup, finalize, and exception handling.
    """
    self.args = args
    self.kwargs = kwargs
    tracker = request.tracker
    request = self.initialize_request(request, *args, **kwargs)
    request.tracker = tracker
    self.request = request
    self.headers = self.default_response_headers  # deprecate?

    try:
        self.initial(request, *args, **kwargs)

        # Get the appropriate handler method
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(),
                              self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        old = time.time()
        response = handler(request, *args, **kwargs)
    except Exception as exc:
        response = self.handle_exception(exc)
    cost_time = time.time() - old
    tracker.create_processes(path=request.path, cost=cost_time, attributes={}, type='Controller')
    self.response = self.finalize_response(request, response, *args, **kwargs)
    return self.response

from SweetPy.extend.response_plus import Response
from django.http.response import HttpResponseBase
from django.utils.cache import cc_delim_re, patch_vary_headers
def finalize_response(self, request, response, *args, **kwargs):
    """
    Returns the final response object.
    """
    # Make the error obvious if a proper response is not returned
    assert isinstance(response, HttpResponseBase), (
        'Expected a `Response`, `HttpResponse` or `HttpStreamingResponse` '
        'to be returned from the view, but received a `%s`'
        % type(response)
    )

    if isinstance(response, Response):
        if not getattr(request, 'accepted_renderer', None):
            neg = self.perform_content_negotiation(request, force=True)
            request.accepted_renderer, request.accepted_media_type = neg

        response.accepted_renderer = request.accepted_renderer
        response.accepted_media_type = request.accepted_media_type
        response.renderer_context = self.get_renderer_context()

    # Add new vary headers to the response instead of overwriting.
    vary_headers = self.headers.pop('Vary', None)
    if vary_headers is not None:
        patch_vary_headers(response, cc_delim_re.split(vary_headers))

    for key, value in self.headers.items():
        response[key] = value

    return response

from rest_framework.views import APIView

APIView.dispatch = dispatch
APIView.finalize_response = finalize_response
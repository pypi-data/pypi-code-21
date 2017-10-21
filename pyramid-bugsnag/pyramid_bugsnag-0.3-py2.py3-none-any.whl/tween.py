import logging

import bugsnag

log = logging.getLogger('pyramid_bugsnag')


def get_route_name(request):
    """Get a route name from URL Dispatch or Traversal."""
    if request.matched_route:
        return request.matched_route.name

    return 'no-matched-route'


def extract_context(request):
    parts = [request.method, get_route_name(request)]
    return ' '.join(parts)


def extract_user(request):
    user_id = (
        request.unauthenticated_userid
        or request.remote_user
        or request.remote_addr
    )
    return {'id': user_id}


def extract_metadata(request):
    return {
        'request': {
            'method': request.method,
            'path': request.path,
            'query_string': request.query_string,
            'GET': dict(request.GET),
            'POST': dict(request.POST),
            'url': request.url,
            'user_agent': request.user_agent,
        }
    }


EXCEPTION_REASON = {
    "type": "unhandledExceptionMiddleware",
    "attributes": {
        "framework": "Pyramid"
    }
}


def handle_error(request, exception):
    try:
        bugsnag.notify(
            exception,
            context=extract_context(request),
            user=extract_user(request),
            metadata=extract_metadata(request),
            severity_reason=EXCEPTION_REASON,
        )
    except Exception:
        log.exception("Error in Bugsnag tween")


def tween_factory(handler, registry):
    def tween(request):
        try:
            response = handler(request)
        except Exception as exc:
            handle_error(request, exc)
            raise

        if request.exception is not None:
            handle_error(request, request.exception)

        return response

    return tween

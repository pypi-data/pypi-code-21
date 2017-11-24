
import json
import logging

from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

__all__ = ('csp_report',)


@csrf_exempt
@require_POST
def csp_report(request: HttpRequest) -> HttpResponse:
    """
    View handling reports by CSP headers. When there is problem by CSP,
    then browser fire request to this view with JSON data describing
    problem. It's simply just logged as warning for later analyzing.
    """
    data = request.read()
    data = json.loads(str(data, 'utf8', 'replace'))
    logging.warning(data)
    return HttpResponse('OK')

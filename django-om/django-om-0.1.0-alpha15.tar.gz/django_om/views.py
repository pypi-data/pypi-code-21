import logging
import traceback

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from transit.transit_types import Symbol

from django_om.parser import Query
from django_om.utils import read_transit, write_transit
import django_om.settings as settings

logger = logging.getLogger('django_om')


@require_POST
@csrf_exempt
def parser(request):
    try:
        if request.FILES and request.POST.get('dispatch-key'):
            meta = request.POST.dict()
            dispatch_key = meta.pop('dispatch-key')
            query = [[
                Symbol(dispatch_key), {
                    'files': request.FILES,
                    'meta': meta
                }
            ]]
        else:
            query = read_transit(request.body)
        parsed_query = Query(query)
        logger.debug(parsed_query)
        result = parsed_query.run(request)
        response = write_transit(result)
        return HttpResponse(response, content_type='application/transit+json')
    except Exception, e:
        default_message = traceback.format_exc() if settings.DEBUG else str(e)
        response = {'server/error': getattr(e, 'details', default_message)}
        redirect = getattr(e, 'redirect', None)
        if redirect:
            response.update(redirect)
        return HttpResponse(
            write_transit(response),
            content_type='application/transit+json',
            status=getattr(e, 'status', 400)
        )

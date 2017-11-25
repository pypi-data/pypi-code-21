from django.conf import settings
from ipware.ip import get_ip
from server_side_piwik.tasks import record_analytic


class PiwikMiddleware(object):
    """ Record every request to piwik """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        SITE_ID = getattr(settings, 'PIWIK_SITE_ID', None)
        if SITE_ID:
            ip = get_ip(request)
            keys_to_serialize = [
                'HTTP_USER_AGENT',
                'REMOTE_ADDR',
                'HTTP_REFERER',
                'HTTP_ACCEPT_LANGUAGE',
                'SERVER_NAME',
                'PATH_INFO',
                'QUERY_STRING',
            ]
            data = {
                'HTTPS': request.is_secure()        
            }
            for key in keys_to_serialize:
                if key in request.META:
                    data[key] = request.META[key]
            record_analytic.delay(data, ip)
        return response

import prometheus_client
from django.http.response import HttpResponse
from django.conf import settings

from . import auth, generate_versions


@auth.basic
def versions_view(request):
    application_labels = getattr(settings, 'VERSIONS_LABELS', {})
    return HttpResponse(
        generate_versions(**application_labels),
        content_type=prometheus_client.CONTENT_TYPE_LATEST)

from django.conf import settings
from celery import shared_task
from piwikapi.tracking import PiwikTracker
from piwikapi.tests.request import FakeRequest


@shared_task
def record_analytic(headers: dict, ip: str):
    """ Send analytics data to piwik """
    # Use "FakeRequest" because we had to serialize the real request
    request = FakeRequest(headers)
    pt = PiwikTracker(settings.PIWIK_SITE_ID, request)
    pt.set_api_url(settings.PIWIK_API_URL)
    if settings.PIWIK_TOKEN_AUTH:
        pt.set_token_auth(settings.PIWIK_TOKEN_AUTH)
        pt.set_ip(ip)
    # Truncate it
    visited_url = request.META['PATH_INFO'][:1000]
    pt.do_track_page_view(visited_url)

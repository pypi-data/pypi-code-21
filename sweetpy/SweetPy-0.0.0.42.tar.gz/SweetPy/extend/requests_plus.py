import requests
from django.conf import settings
from ..setting import sweet_py_version

def request(request,method, url, **kwargs):
    tracker_id = None
    if hasattr(request, 'tracker'):
        tracker = request.tracker
        tracker_id = tracker.tracker_id
    headers = kwargs.get('headers',None)
    if headers is None:
        headers = {}
    if tracker_id:
        headers['X-SWEET-CLOUD-TRACE-ID'] = tracker_id
    headers['X-SWEET-CLOUD-FROM'] = settings.SWEET_CLOUD_APPNAME
    headers['X-SWEET-CLOUD-FROM-INDEX'] = settings.SWEET_CLOUD_APPPORT
    headers['X-SWEET-CLOUD-TARGET'] = ''
    headers['X-SWEET-CLOUD-TARGET-VERSION'] = sweet_py_version
    kwargs['headers'] = headers
    return requests.request(method, url, kwargs)
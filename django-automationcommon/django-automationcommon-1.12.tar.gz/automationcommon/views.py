import logging
import requests
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render
from zeep import Client

LOGGER = logging.getLogger('automationcommon')


@user_passes_test(lambda user: user.is_superuser)
def impersonate(request):
    """
    Renders the page allow an admin to impersonate any user.
    """
    return render(request, 'impersonate.html')


def status(request):
    """
    Checks that all the services (external or internal) used by the Self-Service Gateway are working,
    returning a HTTP 500 if any of them do not work, or a 200 otherwise. It contains individual services checklist
    in the view.
    """

    status_results = {}
    try:
        User.objects.first()
        status_results['Database'] = True
    except:
        status_results['Database'] = False

    overall_result = status_results['Database']

    if hasattr(settings, 'SERVICE_CHECKS'):
        for name, service in settings.SERVICE_CHECKS.items():
            try:
                if isinstance(service, str):
                    # treat as REST endpoint
                    response = requests.get(service)
                    status_results[name] = response.status_code == 200
                else:
                    # assume soap descriptor
                    client = Client(service['url'])
                    proxy = client.bind(service_name=service['name'], port_name=service['name'] + 'Soap12')
                    proxy[service['operation']]()
                    status_results[name] = True
            except Exception as e:
                status_results[name] = False
            overall_result = overall_result and status_results[name]

    if not overall_result:
        LOGGER.error("Status Webpage returning 500: %s" % status_results)

    return render(request, 'status.html', {'status_results': status_results}, status=200 if overall_result else 500)

from django.http import Http404

import logging
from . import settings, models

__author__ = 'Michael'

logger = logging.getLogger('mkdjango.app_manager.intercept')


class AppNameInterceptor(object):
    def __init__(self, get_response):
        self.__get_response = get_response

    def __call__(self, request):
        response = self.__get_response(request)

        app_name = request.resolver_match.app_name
        try:
            app = models.App.objects.get(name=app_name)
        except models.App.DoesNotExist:
            # Not registered in the database
            if settings.APP_MANAGER_INTERCEPT_UNREGISTERED:
                logger.info("Intercepted unregistered app '{}'".format(app_name))
                raise Http404
            return response
        if not app.active:
            logger.info("Intercepted inactive app '{}'".format(app_name))
            raise Http404

        return response

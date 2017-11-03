# coding=utf-8
from datetime import timedelta

from django.utils.timezone import now


try:
    # for Django >= 1.10
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # for Django < 1.10
    MiddlewareMixin = object


class ExposeAutoEnrollMiddleware(MiddlewareMixin):
    """
    Set a cookie that can be read on FE to determine whether an
    experiment is active on any page.
    TODO: make a JS indicator for staff users
    """
    def process_response(self, request, response):
        # TODO do we turn this on only for staff users? Any issues like this?
        experiments = getattr(request, 'experiments', None)
        if experiments and request.user.is_staff:
            response.set_cookie('experiments', experiments.report)
        else:
            if 'experiments' in request.COOKIES:
                in_the_past = now() - timedelta(days=365)
                response.set_cookie('experiments', '', expires=in_the_past)
        return response

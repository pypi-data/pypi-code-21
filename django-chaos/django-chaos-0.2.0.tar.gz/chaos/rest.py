# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.template import Template, TemplateDoesNotExist, loader
from rest_framework.response import Response
from rest_framework import status
from rest_framework import compat
from django_filters.rest_framework import backends


class TempBackend(backends.DjangoFilterBackend):

    # https://github.com/philipn/django-rest-framework-filters/issues/126#issuecomment-254302525
    def to_html(self, request, queryset, view):
        filter_class = self.get_filter_class(view, queryset)
        if not filter_class:
            return None
        filter_instance = filter_class(request.query_params, queryset=queryset)

        # forces `form` evaluation before `qs` is called. This prevents an empty form from being cached.
        filter_instance.form

        try:
            template = loader.get_template(self.template)
        except TemplateDoesNotExist:
            template = Template(backends.template_default)

        return compat.template_render(template,
                                      context={'filter': filter_instance})


class Responses(object):

    """pre baked responses"""

    @staticmethod
    def success(message=_('Request succeded')):
        return Response(
            {'status': 'Succeeded', 'message': message}
        )

    @staticmethod
    def client_error(message=_('Client Error')):
        return Response(
            {'status': 'Not Found', 'message': message},
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def not_found(message=_('Object Not Found')):
        return Response(
            {'status': 'Not Found', 'message': message},
            status=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def server_error(message=_('Server Error')):
        return Response(
            {'status': 'Error', 'message': message},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

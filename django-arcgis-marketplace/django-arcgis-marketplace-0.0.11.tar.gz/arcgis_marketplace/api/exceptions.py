from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import APIException


class ArcgisException(APIException):
    default_detail = _('Arcgis server error')
    default_code = 'arcgis_error'

    def __init__(self, status_code=None, detail=None, code=None):
        self.status_code = status_code
        super().__init__(detail, code)

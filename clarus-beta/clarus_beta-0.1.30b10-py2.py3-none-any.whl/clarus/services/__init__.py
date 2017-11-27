from __future__ import print_function
import clarus
import clarus.api
from clarus.models import ApiResponse, ApiError


def api_request(serviceCategory, service, output=None, **params):
    httpresp = clarus.api.request(serviceCategory, service, output, **params);
    if (httpresp.status_code != 200):
        raise ApiError(httpresp)
    else:
        return ApiResponse(httpresp);

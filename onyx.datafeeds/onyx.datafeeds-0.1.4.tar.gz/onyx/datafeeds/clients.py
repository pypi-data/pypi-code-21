###############################################################################
#
#   Copyright: (c) 2017 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from onyx.core import CurveField, HlocvCurveField
from onyx.core import load_system_configuration

from .exceptions import DatafeedError, SecurityError, FieldError
from .exceptions import NoDataserverAvailable
from .utils import decode_message

import tornado.httpclient
import tornado.httputil

import datetime
import json

__all__ = ["DataClient"]


# -----------------------------------------------------------------------------
def to_upper(v):
    return v.upper() if isinstance(v, str) else v


###############################################################################
class DataClient(object):
    """
    This is a blocking client to send requests to a datafeed router.
    """
    # -------------------------------------------------------------------------
    def __init__(self, address=None, port=None, timeout=60):
        config = load_system_configuration()

        address = address or config.get("datafeed", "router_address")
        port = port or config.getint("datafeed", "router_port")

        self.bdp_url = "http://{0!s}:{1!s}/bbg-bdp/".format(address, port)
        self.bdh_url = "http://{0!s}:{1!s}/bbg-bdh/".format(address, port)
        self.timeout = timeout

    # -------------------------------------------------------------------------
    def BDP(self, sec, field,
            overrides=None, RT=False, fail_after=3):
        # --- ensure security, field, and overrides are upper case as the
        #     request caching is case sensitive
        sec = sec.upper()
        field = field.upper()

        if overrides is None:
            overrides = "null"
        else:
            # --- convert all keys and string-like values to upper case
            overrides = {k.upper(): to_upper(v) for k, v in overrides.items()}
            # --- look for any date-override and convert it to its correct
            #     string representation
            for k, v in overrides.items():
                if isinstance(v, datetime.datetime):
                    overrides[k] = v.strftime("%Y%m%d")
            overrides = json.dumps(overrides)

        request = {
            "sec": sec,
            "field": field,
            "overrides": overrides,
            "RT": RT,
            "type": "BDP",
        }

        response = self.query(self.bdp_url, request)

        return response["payload"]

    # -------------------------------------------------------------------------
    def BDH(self, sec, field, sd, ed,
            adj=True, overrides=None, fail_after=3):
        # --- ensure security, field, and overrides are upper case as the
        #     request caching is case sensitive
        sec = sec.upper()
        field = field.upper()

        if overrides is None:
            overrides = "null"
        else:
            # --- convert all keys and string-like values to upper case
            overrides = {k.upper(): to_upper(v) for k, v in overrides.items()}
            # --- look for any date-override and convert it to its correct
            #     string representation
            for k, v in overrides.items():
                if isinstance(v, datetime.datetime):
                    overrides[k] = v.strftime("%Y%m%d")
            overrides = json.dumps(overrides)

        request = {
            "sec": sec,
            "field": field,
            "start": sd.strftime("%Y%m%d"),
            "end": ed.strftime("%Y%m%d"),
            "adjusted": adj,
            "overrides": overrides,
            "type": "BDH",
        }

        response = self.query(self.bdh_url, request)

        if response["type"] == "Curve":
            return CurveField.from_json(None, response["payload"])
        elif response["type"] == "HlocvCurve":
            return HlocvCurveField.from_json(None, response["payload"])

    # -------------------------------------------------------------------------
    def query(self, base_url, request):
        # --- send http GET request to datafeed router which then dispatches
        #     the request to one of the available datafeed servers
        url = tornado.httputil.url_concat(base_url, request)
        client = tornado.httpclient.HTTPClient()
        try:
            response = client.fetch(url, request_timeout=self.timeout)
        except tornado.httpclient.HTTPError as err:
            if err.code == 503:
                raise NoDataserverAvailable(str(err))
            else:
                raise
        finally:
            client.close()

        response = decode_message(response.body)
        self.manage_exceptions(response)
 
        return response

    # -------------------------------------------------------------------------
    def manage_exceptions(self, response):
        if response["type"] == "TimeoutError":
            raise TimeoutError(response["payload"])
        if response["type"] == "DatafeedError":
            raise DatafeedError(response["payload"])
        if response["type"] == "SecurityError":
            raise SecurityError(response["payload"])
        if response["type"] == "FieldError":
            raise FieldError(response["payload"])
        if response["type"] == "NotImplementedError":
            raise NotImplementedError(response["payload"])

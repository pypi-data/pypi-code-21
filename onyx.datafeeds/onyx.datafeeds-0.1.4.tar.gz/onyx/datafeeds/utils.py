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

from onyx.core.database.ufo_base import custom_encoder, custom_decoder

import json
import hashlib

REQ_FIELDS = ("sec", "field", "start", "end",
              "adjusted", "overrides", "type", "real-time")


# -----------------------------------------------------------------------------
def encode_message(msg):
    encoded_msg = json.dumps(msg, separators=(",", ":"), cls=custom_encoder)
    return bytes(encoded_msg + "\n", "utf-8")


# -----------------------------------------------------------------------------
def decode_message(msg):
    return json.loads(msg.decode("utf-8"), cls=custom_decoder)


# -----------------------------------------------------------------------------
def request_to_uid(request, real_time):
    # --- serialize request making sure we always get the same key for the
    #     same request (NB: the request is a dictionary which means
    #     ordering is not guaranteed).
    req_vls = ["({0!s}".format(request.get(k, None)) for k in REQ_FIELDS]
    req_vls.append("{0!s}".format(real_time))
    return hashlib.sha1("".join(req_vls).encode("utf-8")).hexdigest()

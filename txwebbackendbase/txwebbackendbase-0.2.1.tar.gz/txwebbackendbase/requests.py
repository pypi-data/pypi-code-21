"""
Request is a request
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json


def dejsonify(request):
    json_content = request.content.read()
    if json_content:
        content = json.loads(json_content)
    else:
        content = {}
    return content


def jsonify(request, data):
    request.responseHeaders.addRawHeader("content-type", "application/json")
    return json.dumps(data, indent=4, sort_keys=True, separators=(',', ': '))

# Copyright (c) 2017, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from datetime import datetime

import json

class ParameterValidationResult:
    """Represents an analysis template execution validation result to the server

    :param str type: If this result is INFO, WARNING, or ERROR
    :param str message: The the message
    :param str details: (optional) Detailed message about the result
    :param str parameter_id: (optional) the analysis template parameter that this progress update refers to

    :var str type: If this result is INFO, WARNING, or ERROR
    :var str message: The the message
    :var str details: (optional) Detailed message about the result
    :var str parameter_id: (optional) the analysis template parameter that this progress update refers to
    """

    def __init__(self, type, message=None, details=None, parameter_id=None):
        """For internal use only"""
        self.type     = type
        self.message  = message
        self.details = details
        self.parameter_id = parameter_id

    def _from_json(self, body):
        """For internal use only -- sets from json message body"""
        self.type         = body.get('type')
        self.message      = body.get('message')
        self.details      = body.get('details')
        self.parameter_id = body.get('parameter_id')


    def _to_json(self):
        body = {}

        if not hasattr(self, 'type'):
            raise ValueError('Must specify a type of parameter validation result')
        if not self.type in {'INFO', 'WARNING', 'ERROR'}:
            raise ValueError('type must be INFO, WARNING, ERROR, not ' + str(self.type))
        body['type'] = self.type;

        if (not self.message):
            raise ValueError('message must be specified in parameter validation result')

        body['message'] = self.message

        if (self.details):
            body['details'] = self.details
        if (self.parameter_id):
            body['parameter_id'] = self.parameter_id

        return body

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

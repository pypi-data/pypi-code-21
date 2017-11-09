# Copyright 2016 Internap.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class UbersmithException(Exception):
    code = None
    message = None

    def __init__(self, code=None, message=None):
        self.code = code
        self.message = message

    def __str__(self):
        return 'Error code {0} - message: {1}'.format(self.code, self.message)


def get_exception_for(status_code):
    exception_class = {
        400: BadRequest,
        401: Unauthorized,
        403: Forbidden,
        404: NotFound
    }
    return exception_class.get(status_code, UnknownError(status_code))


class BadRequest(UbersmithException):
    def __init__(self):
        super(BadRequest, self).__init__(code=400, message='The server could not comply with the request since '
                                                           'it is either malformed or otherwise incorrect.')


class Forbidden(UbersmithException):
    def __init__(self):
        super(Forbidden, self).__init__(code=403,
                                        message='The server understood the request, but is refusing to fulfill it.')


class NotFound(UbersmithException):
    def __init__(self):
        super(NotFound, self).__init__(code=404, message='The requested resource could not be found.')


class Unauthorized(UbersmithException):
    def __init__(self):
        super(Unauthorized, self).__init__(code=401, message='This request requires user authentication')


class UnknownError(UbersmithException):
    def __init__(self, code):
        super(UnknownError, self).__init__(code=code, message='An unknown error occurred')


class UbersmithConnectionError(UbersmithException):
    def __init__(self, url):
        super(UbersmithConnectionError, self).__init__(message='Could not connect to {0}'.format(url))


class UbersmithTimeout(UbersmithException):
    def __init__(self, url, timeout):
        super(UbersmithTimeout, self) \
            .__init__(
            message='Trying to connect to {url} timed out after {timeout} seconds'.format(url=url, timeout=timeout))

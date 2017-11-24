# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2016-2017 GiovanniMCMXCIX

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


class ConnectException(Exception):
    """Base exception class for connect.py"""
    pass


class HTTPSException(ConnectException):
    """Exception that's thrown when an HTTP request operation fails."""
    def __init__(self, message, response=None):
        self.response = response
        self.message = message
        if not self.response:
            fmt = '{1}'
        else:
            fmt = '{0.reason} (status code: {0.status_code})'

        if self.message and self.response:
            fmt += ': {1}'

        super().__init__(fmt.format(self.response, self.message))


class Unauthorized(HTTPSException):
    """Exception that's thrown for when status code 401 occurs."""
    pass


class Forbidden(HTTPSException):
    """Exception that's thrown for when status code 403 occurs."""
    pass


class NotFound(HTTPSException):
    """Exception that's thrown for when status code 404 occurs."""
    pass

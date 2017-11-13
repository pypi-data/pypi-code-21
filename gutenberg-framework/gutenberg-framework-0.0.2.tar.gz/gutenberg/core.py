import enum;
import requests;
import simplejson;
from gutenberg.matcher import *;

class when:

    def __init__(self, method, url, body=None):
        self.method = method;
        self.url = url;
        self.body = body;

    def withBody(self, body):
        self.body = body;

    def expect(self, status, body, andNothingMore=False):
        try:
            response = doRequest(self.method, self.url, self.body);
            when._assertEquals("wrong status", status.value, response.status_code);
            for key, expectedValue in body.items():
                when._assertEquals(key, expectedValue, response.json().get(key));
            if andNothingMore:
                when._assertEquals("found too many attributes", body.keys(), response.json().keys());
        except requests.exceptions.ConnectionError:
            raise AssertionException("Could not establish connection");
        except simplejson.scanner.JSONDecodeError:
            raise AssertionException("Did not receive JSON value");

    def _assertEquals(message, expected, actual):
        if (isMatcher(expected)):
            if (not expected.matches(actual)):
                exceptionMessage = message +"""
expected {},
but received <<<
{}
>>>
""".format(expected.name, actual);
                raise AssertionException(exceptionMessage);

        elif (expected != actual):
            exceptionMessage = message + "\n" + "expected <<<\n";
            exceptionMessage += str(expected) + "\n";
            exceptionMessage += ">>>\n\n";
            exceptionMessage += "but received <<<\n";
            exceptionMessage += str(actual) + "\n";
            exceptionMessage += ">>>\n";
            raise AssertionException(exceptionMessage);

class AssertionException(Exception):
    pass;

class Status(enum.Enum):
    ANY = 0;
    OK = 200;
    CREATED = 201;
    ACCEPTED = 202;
    BAD_REQUEST = 400;
    FORBIDDEN = 403;
    NOT_FOUND = 404;
    METHOD_NOT_ALLOWED = 405;
    INTERNAL_SERVER_ERROR = 500;


class Method(enum.Enum):
    GET = 0;
    POST = 1;
    PUT = 2;
    DELETE = 3;


__methodFunctions = {
    Method.GET : requests.get,
    Method.POST : requests.post,
    Method.PUT : requests.put,
    Method.DELETE : requests.delete,
}



def doRequest(method, url, body):
    return __methodFunctions[method](url, json=body);

andNothingMore = True;

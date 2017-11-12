import enum;
import requests;
import simplejson;

class when:

    def __init__(self, method, url, body=None):
        self.method = method;
        self.url = url;
        self.body = body;

    def withBody(self, body):
        self.body = body;

    def expect(self, status, body):
        try:
            response = doRequest(self.url, self.method, self.body);
            when.__assertEquals("wrong status", status.value, response.status_code);
            when.__assertEquals("wrong body", body, response.json());
        except requests.exceptions.ConnectionError:
            print("Could not establish connection");
        except simplejson.scanner.JSONDecodeError:
            print("Did not receive JSON value");

    def __assertEquals(message, expected, actual):
        if (expected != actual):
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



def doRequest(url, method, body):
    return __methodFunctions[method](url, json=body);

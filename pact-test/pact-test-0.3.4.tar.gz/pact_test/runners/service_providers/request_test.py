from pact_test.utils.logger import *
from pact_test.either import *
from pact_test.models.request import PactRequest
from pact_test.models.response import PactResponse
from pact_test.servers.mock_server import MockServer
from pact_test.matchers.request_matcher import match


def verify_request(decorated_method, port=9999):
    mock_response = build_expected_response(decorated_method)
    debug('Build Mock Response: DONE')
    expected_request = build_expected_request(decorated_method)
    debug('Build Expected Request: DONE')

    mock_server = MockServer(mock_response=mock_response, port=port)
    debug('Build Mock Server: DONE')
    mock_server.start()
    debug('Start Mock Server: DONE')
    decorated_method()
    debug('Execute Test: DONE')
    mock_server.shutdown()
    debug('Shutdown Mock Server: DONE')
    report = mock_server.report()
    debug('Fetch Report From Mock Server: DONE')

    if len(report) is 0:
        return Left('Missing request(s) for "' + format_message(decorated_method) + '"')
    actual_request = build_actual_request(report[0])
    debug('Build Actual Request: DONE')
    return match(actual_request, expected_request)


def build_expected_response(decorated_method):
    return PactResponse(
        body=decorated_method.will_respond_with.get('body'),
        status=decorated_method.will_respond_with.get('status'),
        headers=decorated_method.will_respond_with.get('headers')
    )


def build_expected_request(decorated_method):
    return PactRequest(
        method=decorated_method.with_request.get('method'),
        body=decorated_method.with_request.get('body'),
        headers=decorated_method.with_request.get('headers'),
        path=decorated_method.with_request.get('path'),
        query=decorated_method.with_request.get('query')
    )


def build_actual_request(request):
    return PactRequest(
        path=request.get('path'),
        query=request.get('query'),
        method=request.get('method'),
        body=request.get('body'),
        headers=request.get('headers')
    )


def format_message(decorated_method):
    return 'given ' + \
           decorated_method.given + \
           ', upon receiving ' + \
           decorated_method.upon_receiving

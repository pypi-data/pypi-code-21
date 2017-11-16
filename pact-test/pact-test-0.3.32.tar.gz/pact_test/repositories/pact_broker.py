import json
import requests
from pact_test.either import *
from pact_test.utils.logger import debug


PACT_BROKER_URL = 'http://localhost:9292/'


def upload_pact(provider_name, consumer_name, pact, base_url=PACT_BROKER_URL):
    print()
    pact = format_headers(pact)
    debug(pact)
    current_version = get_latest_version(consumer_name)
    debug(current_version.value)
    if type(current_version) is Right:
        v = next_version(current_version.value)
        debug(v)
        try:
            url = base_url + 'pacts/provider/' + provider_name + '/consumer/' + consumer_name + '/version/' + v
            debug(url)
            payload = json.dumps(pact)
            debug(payload)
            headers = {'content-type': 'application/json'}
            debug(headers)
            response = requests.put(url, data=payload, headers=headers)
            debug(response.status_code)
            return Right(response.json())
        except requests.exceptions.ConnectionError as e:
            msg = 'Failed to establish a new connection with ' + base_url
            debug(msg)
            return Left(msg)
    print()


def get_latest_version(consumer_name, base_url=PACT_BROKER_URL):
    try:
        url = base_url + 'pacticipants/' + consumer_name + '/versions/'
        response = requests.get(url)
        if response.status_code is not 200:
            return Right('1.0.0')
        return Right(response.json()['_embedded']['versions'][0]['number'])
    except requests.exceptions.ConnectionError as e:
        msg = 'Failed to establish a new connection with ' + base_url
        debug('[get_latest_version] - ' + msg)
        return Left(msg)


def next_version(current_version='1.0.0'):
    versions = current_version.split('.')
    next_minor = str(1 + int(versions[-1]))
    return '.'.join([versions[0], versions[1], next_minor])


def format_headers(pact):
    for interaction in pact.get('interactions', []):
        req_headers = interaction.get('request').get('headers')
        fixed_req_headers = {}
        for h in req_headers:
            fixed_req_headers.update(h)
        interaction['request']['headers'] = fixed_req_headers

        res_headers = interaction.get('response').get('headers')
        fixes_req_headers = {}
        for h in res_headers:
            fixes_req_headers.update(h)
        interaction['response']['headers'] = fixes_req_headers
    return pact

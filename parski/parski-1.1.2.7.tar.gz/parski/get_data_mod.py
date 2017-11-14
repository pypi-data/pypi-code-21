from __future__ import print_function
from os import environ
from time import sleep
import json
import requests


API_RETRY = 3

def get_data(url=None, file_name='output.json', source="file", key_var="PCT_API_READ_KEY", silent=False):
    '''
    Load data from either a source file or the api
    '''
    if source == "file":
        try:
            if not silent:
                print("Loading File...")
            with open(file_name, 'rb') as stored_file:
                data = stored_file.read()
                return {'status_code': 200, 'error_msg': None, 'data': json.loads(data)}
        except Exception as error:
            if not silent:
                print("File could not be loaded.  Pulling from api")
            if url is None:
                return {'status_code': 404, 'error_msg': 'File could not be loaded', 'data': None}
            return _api_load(url, file_name, silent=silent)
    elif source == "api":
        return _api_load(url, file_name, key_var, silent=silent)
    else:
        return {'status_code': 500, 'error_msg': "Invalid source parameter.", 'data': None}

def _write_data(data, file_name='output.json', silent=False):
    with open(file_name, 'wb') as output_file:
        output_file.write(json.dumps(data, sort_keys=True, indent=4))
        output_file.close()
        if not silent:
            print("File written successfully...")

def _api_load(url, file_name='output.json', key_var="PCT_API_READ_KEY", silent=False):
    return_request = {}
    return_request['data'] = []
    return_request['error_msg'] = None
    return_request['status_code'] = 200
    try:
        API_KEY = environ[key_var]
    except KeyError:
        return_request['status_code'] = 401
        return_request['error_msg'] = key_var + ' could not be loaded.  Unauthorized.'
        return_request['data'] = None
        return return_request
    headers = {
        'x-api-key': API_KEY,
        'Cache-Control': 'no-cache'
    }
    response, resp_headers = _api_try(url, headers, None, silent=silent)
    if response['data'] is None:
        return response

    # Get page count, output if none
    try:
        page_count = int(resp_headers.get("x-pagination-page-count"))
    except:
        if not silent:
            print("No page count specified.  Writing Single Page...")
        json_string = response['data']
        if json_string is None:
            return response
        else:
            clean_json_string = '[' + json_string.lstrip('[').rstrip(']') + ']'
            _write_data(json.loads(clean_json_string), file_name=file_name, silent=silent)
    if not silent:
        print("%s pages to be downloaded" % page_count)
    for page in range(1, page_count+1):
        response, response_headers = _api_try(url, headers, page, silent=silent)
        if response['data']:
            json_string = response['data']
            clean_json_string = '[' + json_string.lstrip('[').rstrip(']') + ']'
            return_request['data'] = return_request['data'] + json.loads(clean_json_string)
        else:
            return response
    if not silent:
        print(page_count)
    _write_data(return_request['data'], file_name=file_name, silent=silent)
    return return_request


def _api_try(url, headers, page=None, silent=False):
    tries = 0
    if page and not silent:
        print("\nPage: %s" % page)
    while tries < API_RETRY:
        if not silent:
            print("Sending API request")
        response, resp_headers = _api_call(url, headers, page, silent=silent)
        if response['error_msg'] and not silent:
            print(response['error_msg'])
        if response['status_code'] == 401 or response['status_code'] == 404:
            return response, None
        if response['data'] and not silent:
            print("Returned Successfully")
            return response, resp_headers
        if not silent:
            print("Trying again in %s seconds\n" % ((tries+1)**2))
        sleep((tries+1)**2)
        if not silent:
            print("LET'S DO THIS!!!!")
        tries += 1

    response['error_msg'] = "Amount of Fails Exceeded.  The API just doesn't want to talk to you today."
    return response, resp_headers


def _api_call(url, headers, page=None, silent=False):
    return_request = {}
    return_request['data'] = None
    return_request['error_msg'] = None

    if page is not None:
        url += "?Page=" + str(page)
    try:
        if not silent:
            print ("GET %s" % url)
        req = requests.get(url, headers=headers)
    except:
        return_request['error_msg'] = 'API Server could not be reached'
        return_request['status_code'] = 404
        return return_request, None
    if req.status_code == 404:
        return_request['error_msg'] = 'API Server could not be reached'
        return_request['status_code'] = 404
        return return_request, None

    return_request['status_code'] = req.status_code
    if req.status_code != 200 and not silent:
        print("WARNING:  API call status code was %s" % req.status_code)

    if req.status_code == 401:
        return_request['error_msg'] = "Unauthorized.  Your API key isn't working..."
    elif req.status_code == 404:
        return_request['error_msg'] = "Not found.  Your url is probably wrong or you're not on VPN"
    elif req.status_code == 502:
        return_request['error_msg'] = "The response failed.  This happens from time to time..."
    elif req.status_code == 503:
        return_request['error_msg'] = "Internal Server Error.  The API might be down..."
    else:
        try:
            return_request['data'] = json.dumps(req.json())
        except:
            return_request['error_msg'] = 'Returned request could not be converted to json'

    return return_request, req.headers


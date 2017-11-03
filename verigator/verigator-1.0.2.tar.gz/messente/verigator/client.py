import requests

from messente.verigator import exceptions


class RestClient(object):
    """Simple http client that handles authentication and content-type
        by default for post and put calls. Default headers are
        content-type: application/json and accept: application/json, however they can be override

    Note: If server returns any other status code except 2xx, client will raise appropriate exception


    Attributes:
        endpoint (str): server url, any other paths will be appended to it
        auth_header (dict): default headers for each request (contains only auth header)
    """

    def __init__(self, endpoint, username, password):
        """

        Args:
            endpoint (str): server url, any other paths will be appended to it
            username (str): used for authentication
            password (str): used for authentication
        """
        self.endpoint = endpoint
        self.auth_header = {
            "X-Service-Auth": ":".join([username, password])
        }
        self.content_type_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get(self, path, params=None, headers=None):
        """
        Wrapper around requests get method
        Args:
            path (str): request path
            params (dict): url parameters
            headers (dict): additional headers

        Returns:
            dict: response body
        """
        new_headers = self.__merge_dicts(self.auth_header, headers)
        return self._request("GET", self.__url(path), params=params, headers=new_headers)

    def post(self, path, headers=None, json=None):
        """
        Wrapper around requests post method
        Args:
            path (str): request path
            headers (dict): additional headers
            json (dict): request payload

        Returns:
            dict: response body
        """
        new_headers = self.__merge_dicts(self.auth_header, self.content_type_headers)
        new_headers = self.__merge_dicts(new_headers, headers)
        return self._request("POST", self.__url(path), headers=new_headers, json=json)

    def put(self, path, headers=None, json=None):
        """
        Wrapper around requests put method
        Args:
            path (str): request path
            headers (dict): additional headers
            json (dict): request payload

        Returns:
            dict: response body
        """
        new_headers = self.__merge_dicts(self.auth_header, self.content_type_headers)
        new_headers = self.__merge_dicts(new_headers, headers)
        return self._request("PUT", self.__url(path), headers=new_headers, json=json)

    def delete(self, path, headers=None):
        """
        Wrapper around requests delete method
        Args:
            path (str): request path
            headers (dict): additional headers

        Returns:
            dict: response body
        """
        new_headers = self.__merge_dicts(self.auth_header, headers)
        return self._request("DELETE", self.__url(path), headers=new_headers)

    def __url(self, path):
        return "/".join([self.endpoint.strip("/"), path])

    @staticmethod
    def __merge_dicts(first, second):
        try:
            new_headers = first.copy()
        except AttributeError:
            new_headers = {}

        try:
            new_headers.update(second)
        except TypeError:
            pass

        return new_headers

    @staticmethod
    def _request(method, path, params=None, headers=None, json=None):
        resp = requests.request(method, path, params=params, headers=headers, json=json)

        status_code = resp.status_code
        try:
            resp_json = resp.json()
        except ValueError:
            raise exceptions.InvalidResponseError(0, resp.text)

        message = resp_json.get('message', None)

        if status_code == 400:
            raise exceptions.InvalidDataError(400, message)
        elif status_code == 401:
            raise exceptions.WrongCredentialsError(401, message)
        elif status_code == 403:
            raise exceptions.ResourceForbiddenError(403, message)
        elif status_code == 404:
            raise exceptions.NoSuchResourceError(404, message)
        elif status_code == 409:
            raise exceptions.ResourceAlreadyExistsError(409, message)
        elif status_code == 422:
            raise exceptions.InvalidDataError(422, message)
        elif status_code == 500:
            raise exceptions.InternalError(500, resp_json)
        elif 300 <= status_code <= 600:
            raise exceptions.VerigatorError(status_code, resp_json)

        return resp_json

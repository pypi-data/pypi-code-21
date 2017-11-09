"""Client library for the transfer API.

See the
[specification](https://git.lumc.nl/j.k.vis/transfer/blob/v1/specs.yaml) for
more information.
"""
import json
import requests
import requests_toolbelt
import sys
import urllib3


class TransferClient(object):
    _version = 'v1'

    def __init__(self, server_name, verify=True, ca_bundle=None, cert=None):
        """Initialisation.

        :arg str server_name: Name or IP of the transfer server.
        :arg bool verify: SSL server certificate verification.
        :arg tuple cert: Client certificate and key paths.
        """
        self.server_name = server_name
        self._cert = cert

        # The requests library takes an 'verify' argument, that can either be a
        # boolean (disable/enable ssl checks), or a path to a CA cert bundle
        # file (which implies 'True').
        # Alternatively, the bundle can be specified in the REQUESTS_CA_BUNDLE
        # environment variable.
        if ca_bundle and verify:
            verify = ca_bundle
        self._verify = verify

        if not self._verify:
            try:
                requests.packages.urllib3.disable_warnings()
            except AttributeError:
                try:
                    urllib3.disable_warnings()
                except AttributeError:
                    sys.stderr = open('/dev/null')


    def _request(
            self, method, endpoint, headers=None, data=None, json=None,
            params=None):
        """Handle a request.

        :arg str method: Method for the request.
        :arg str endpoint: API endpoint.
        :arg dict headers: Dictionary of HTTP Headers to send with the request.
        :arg dict data: Dictionary of file like objects for multipart encoding
            upload.
        :arg dict json: JSON data to send in the body of the request.

        :returns dict: JSON encoded content of the response.
        """
        try:
            response = requests.request(
                method, 'https://{}/{}/{}'.format(
                    self.server_name, self._version, endpoint),
                headers=headers, data=data, json=json, params=params,
                cert=self._cert, verify=self._verify)
        except requests.exceptions.SSLError:
            raise OSError('SSL error, no server certificate installed?')
        if not response.ok: # FIXME: Look at json attribute, use custom error.
            raise ValueError(response.json())
        return response.json()

    def about(self):
        """Returns general information about the server."""
        return self._request('get', 'about')

    def consumer(self, project_name):
        """Returns consumer information for a project."""
        return self._request(
            'get', 'projects/{}/consumer'.format(project_name))

    def consumer_transfers(self, project_name):
        """Returns a transfer resource collection."""
        return self._request(
            'get', 'projects/{}/consumer/transfers'.format(project_name))

    def consumer_transfer(self, project_name, transfer_id):
        """Returns a transfer resource."""
        return self._request(
            'get', 'projects/{}/consumer/transfers/{}'.format(
            project_name, transfer_id))

    def producer(self, project_name):
        """Returns producer information (JSON schema)."""
        return self._request(
            'get', 'projects/{}/producer'.format(project_name))

    def producer_transfers(self, project_name):
        """Returns a transfer resource collection."""
        return self._request(
            'get', 'projects/{}/producer/transfers'.format(project_name))

    def producer_transfer_start(self, project_name, metadata):
        """Initiates a new transfer."""
        return self._request(
            'post', 'projects/{}/producer/transfers'.format(project_name),
            json=metadata)

    def producer_transfer(self, project_name, transfer_id):
        """Returns a transfer resource."""
        return self._request(
            'get', 'projects/{}/producer/transfers/{}'.format(
                project_name, transfer_id))

    def producer_transfer_cancel(self, project_name, transfer_id):
        """Cancels a transfer."""
        return self._request(
            'put', 'projects/{}/producer/transfers/{}'.format(
                project_name, transfer_id),
            json={'status': 'cancelled'})

    def producer_upload(self, project_name, transfer_id, file_handle):
        """Uploads a file."""
        multipart = requests_toolbelt.MultipartEncoder(
            fields={'upload': (file_handle.name, file_handle)})
        return self._request(
            'post', 'projects/{}/producer/transfers/{}/upload'.format(
                project_name, transfer_id),
            {'Content-Type': multipart.content_type}, multipart)

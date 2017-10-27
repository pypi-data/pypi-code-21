import logging
from datetime import datetime, date, timedelta
import json

from requests import get, codes
from requests.exceptions import MissingSchema, InvalidSchema, ConnectionError, InvalidURL

class DynamatError(Exception): pass


log = logging.getLogger('dynamat2050')

# 'url': 'https://subdomain.dynamat2050.com/ProductService.svc',
# 'username': '',
# 'password': ''

class Client():

    def __init__(self, url=None, username=None, password=None, **kwargs):
        self.url = url
        self.headers = {"Accept": "application/json"}
        self.fmt = "%Y-%m-%d %H:%M:%S"
        self.auth = (username, password)

    def test(self):
        response = self.get('meterlist') # potentially raises exceptions
        return {'status': 'OK', 'message': 'Successfully connected'}

    def meters(self):
        response = self.get('meterlist') # potentially raises exceptions
        return [{
            'identifier': m['MeterId'],
            'label': m['Description'].strip()
        } for m in response.json()]

    def meter_data(self, meter_id, from_, to_):
        response = self.consumption(meter_id, from_, to_, "Minute", 30)
        try:
            data = response.json()
        except:
            print(response)
        if data:
            if isinstance(data, list) and len(data) == 1:
                data = data[0]
            return json.dumps(data).encode('utf-8')

    def consumption(self, meter_id, from_, to, interval, n_intervals):
        """Make an actual request for energy data to the server at %url"""
        payload = {
            "ID": meter_id,
            "from": from_.strftime(self.fmt),
            "to": to.strftime(self.fmt),
            "interval": interval,
            "intervalQty": n_intervals
        }
        return self.get('Consumption', params=payload)

    def get(self, endpoint, headers=None, **kwargs):
        """make requests relative to the base_url
        merge default headers
        include any etag passed as an If-Match header"""
        headers = headers or {}
        headers.update(self.headers)
        url = "{}/{}".format(self.url, endpoint)
        try:
            response = get(url, headers=headers, auth=self.auth, verify=False, **kwargs) # verify is set to false for self-signed https
        # except SSLError:
        #     raise InvalidCertificate()
        except ConnectionError as exc:
            try:
                connect_to_google()
            except ConnectionError as e:
                raise DynamatError("Could not connect - check network")
            raise DynamatError("Could not connect - check url")
        except (MissingSchema, InvalidSchema):
            raise DynamatError("Missing schema in url (e.g. https://)")
        except InvalidURL:
            raise DynamatError("Invalid url: '{}'".format(self.url))

        if response.status_code == codes.unauthorized:
            raise DynamatError("Invalid credentials")
        if response.status_code == codes.bad_request:
            raise DynamatError("Bad request")
        if response.status_code == codes.not_found:
            raise DynamatError("Not found: {}".format(response.url))
        if response.status_code == codes.forbidden:
            raise DynamatError("Unauthorised")
        if response.status_code == codes.server_error:
            raise DynamatError("Problem with Dynamat server")
        return response

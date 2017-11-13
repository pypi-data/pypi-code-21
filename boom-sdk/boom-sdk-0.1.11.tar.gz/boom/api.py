import os
import uuid

import requests
import six


class API(object):
    urls = {
        "index": "/",
        "account": "/account/{client}",
        "authenticate": "/account/authenticate",
        "client": "/client/{client}",
        "client-location": "/client/{client}/location/{location}",
        "client-location-experience": "/client/{client}/location/{location}/experience/{experience}",
        "client-location-platform": "/client/{client}/location/{location}/platform/{platform}",
        "conversation": "/conversation/{conversation}",
        "conversation-link": "/conversation/{conversation}/link/{code}",
        "experience": "/experience/{experience}",
        "message": "/message/{message}",
        "platform": "/platform/{platform}",
        "order": "/order/{order}",
        "order-search": "/order/search"
    }

    def __init__(self):
        self.api_url = self.url = os.getenv("BOOM_API_URL", "https://api.boomletsgo.com")

    def get_headers(self):
        return {
            "Content-Type": "application/json"
        }

    def make_url(self, path, querystring=None):
        if path.startswith("/"):
            path = path[1:]

        if querystring:
            querystring = "?{0}".format(six.moves.urllib.parse.urlencode(querystring))
        else:
            querystring = ""

        return "{0}/{1}{2}".format(self.url, path, querystring)

    def generate_endpoint_url(self, endpoint, data=None, **kwargs):
        # Normalize the URL
        path = self.urls.get(endpoint, "")
        if path.startswith("/"):
            path = path[1:]

        querystring = {}
        data = data or {}

        # Replace all tokens in the API URL with the values from data
        for key, value in six.iteritems(kwargs):
            path, updated = self.update_path(path, key, value)
            if not updated and value:
                querystring[key] = value

        for key, value in six.iteritems(data):
            path, updated = self.update_path(path, key, value)

        # If the path ends with a token, that means we are probably creating
        # and don't have a specific item we are working with. Remove the trailing token.
        if path.endswith("}"):
            path = path[0:path.rfind("/")]

        url = self.make_url(path, querystring)
        return url

    def update_path(self, path, key, value):
        # Wrap the key in {}, like client => {client}
        updated = False
        if key.endswith("_id"):
            key = key[:-3]
        token = "{" + key + "}"
        if token in path:
            updated = True
            path = path.replace(token, value)

        return path, updated

    def normalize_data(self, data):
        if isinstance(data, dict):
            data = [data]

        return data

    def get(self, endpoint, **kwargs):
        url = self.generate_endpoint_url(endpoint, **kwargs)
        headers = self.get_headers()
        dataset = requests.get(url, headers=headers)
        dataset = dataset.json()
        dataset = self.normalize_data(dataset)

        return dataset

    def post(self, endpoint, data, **kwargs):
        headers = self.get_headers()
        data = self.normalize_data(data)
        url = self.generate_endpoint_url(endpoint, **kwargs)
        dataset = requests.post(url, headers=headers, json=data)
        dataset = dataset.json()

        return dataset

    def patch(self, endpoint, data, **kwargs):
        headers = self.get_headers()
        data = self.normalize_data(data)
        url = self.generate_endpoint_url(endpoint, **kwargs)
        dataset = requests.patch(url, headers=headers, json=data)
        dataset = dataset.json()

        return dataset

    def delete(self, endpoint, data, **kwargs):
        headers = self.get_headers()
        data = self.normalize_data(data)
        url = self.generate_endpoint_url(endpoint, **kwargs)
        requests.delete(url, headers=headers, json=data)

        return True

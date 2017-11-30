import json

import requests

from ..exceptions import APIError, reraise
from .collections import AddressableCollection


class BaseFileCollection(AddressableCollection):
    def make_item(self, **kwargs):
        return File(
            client=self.client,
            file_id=kwargs['id'],
            name=kwargs['name'],
            file_type=kwargs['type'],
            )


class FileCollection(BaseFileCollection):
    url_path = 'files/'

    def create(self, name):
        """
        Create a SOURCE file with the specified name.
        """
        data = {
            'name': name,
            'type': 'SOURCE',
        }
        try:
            response = self.client.api_post(
                path='files',
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'},
            ).json()
        except requests.RequestException:
            reraise(APIError)
        return self.make_item(**response)


class File(object):
    def __init__(self, client, file_id, name, file_type):
        self.client = client
        self.id = file_id
        self.name = name
        self.type = file_type

    def __repr__(self):
        return '<File {}: {}>'.format(self.id, self.name)

    def __eq__(self, other):
        return all((
            self.client == other.client,
            self.id == other.id,
            self.name == other.name,
            self.type == other.type,
            ))

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def url_path(self):
        return FileCollection(self.client).item_url_path(self.id)

    @property
    def content(self):
        path = '{}/content'.format(self.url_path)
        try:
            response = self.client.api_get(path, stream=True)
        except requests.RequestException as exc:
            if exc.response.status_code == 404:
                content = None
            else:
                reraise(APIError)
        else:
            content = response.content
        return content

    @content.setter
    def content(self, value):
        path = '{}/content'.format(self.url_path)
        try:
            self.client.api_put(path, data=value)
        except requests.RequestException:
            reraise(APIError)

    def delete(self):
        try:
            self.client.api_delete(self.url_path)
        except requests.RequestException:
            reraise(APIError)

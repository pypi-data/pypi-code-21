import requests
import json


class Gist(object):
    def __init__(self, token):
        self._token = token
        self._baseurl = 'https://api.github.com/gists/'

    def get(self, gist_id, filename):
        r = requests.get(
            self._gist_url(gist_id),
            headers=self._headers()
        )
        r.raise_for_status()
        data = json.loads(r.text)
        return data['files'][filename]['content']

    def update(self, gist_id, filename, content, description=''):
        r = requests.post(
            self._gist_url(gist_id),
            json.dumps({
                'description': description,
                'files': {
                    filename: {
                        'content': content,
                    }
                },
            }),
            headers=self._headers()
        )
        r.raise_for_status()

    def _headers(self):
        return {
            'Authorization': 'token ' + self._token,
            "Content-Type": "application/json"
        }

    def _gist_url(self, gist_id):
        return self._baseurl + gist_id

import json
import re

from django.core.handlers.wsgi import WSGIRequest
from django.utils.encoding import force_text


class ExtendedWSGIRequest(WSGIRequest):
    json_mime_type_regex = r'^application/(.*\+)?json$'

    def _load_json(self):
        self._json = {}
        if self.method not in ['POST', 'PUT', 'PATCH']:
            return
        if self._read_started and not hasattr(self, '_body'):
            self._post_parse_error = True
            return

        if re.match(self.json_mime_type_regex, self.content_type):
            try:
                self._json = json.loads(force_text(self.body))
            except:
                self._post_parse_error = True

    def _get_json(self):
        if not hasattr(self, '_json'):
            self._load_json()
        return self._json

    def _set_json(self, json):
        self._json = json

    json = property(_get_json, _set_json)

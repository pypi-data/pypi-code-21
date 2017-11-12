import json
import re

from django.apps import AppConfig
from django.core.handlers.wsgi import WSGIHandler
from django.utils.encoding import force_text


class DjangoExtendedJsonConfig(AppConfig):
    name = 'djext.json'
    verbose_name = 'JSON tools'

    def ready(self):
        self.wrap_request()

    def wrap_request(self):
        json_mime_type_regex = r'^application/(.*\+)?json$'

        def _load_json(_self):
            _self._json = {}
            if _self.method not in ['POST', 'PUT', 'PATCH']:
                return
            if _self._read_started and not hasattr(_self, '_body'):
                _self._post_parse_error = True
                return

            if re.match(json_mime_type_regex, _self.content_type):
                try:
                    _self._json = json.loads(force_text(_self.body))
                except:
                    _self._post_parse_error = True

        def _get_json(_self):
            if not hasattr(_self, '_json'):
                _load_json(_self)
            return _self._json

        def _set_json(_self, json):
            _self._json = json

        setattr(WSGIHandler.request_class, 'json', property(_get_json, _set_json))

from typing import (
    Callable,
    Optional,
)

import pyramid.config
import pyramid.renderers
import pyramid.request
import pyramid.response

__author__ = "Motoki Naruse"
__copyright__ = "Motoki Naruse"
__credits__ = ["Motoki Naruse"]
__email__ = "motoki@naru.se"
__license__ = "MIT"
__maintainer__ = "Motoki Naruse"
__version__ = '0.0.1'


class JsonResponse:
    def __init__(self) -> None:
        self.json_renderer = pyramid.renderers.JSON()

    def _dump_json(self, source, request: Optional[pyramid.request.Request]) -> str:
        return self.json_renderer(None)(source, {'request': request} if request else {})

    def dump_json(self, request: pyramid.request.Request, source) -> str:
        return self._dump_json(source, None)

    def response_json(self, request: pyramid.request.Request, body, status=None) -> Callable:
        json_body = self._dump_json(body, request)

        return pyramid.response.Response(
            json_body,
            status=status,
            headerlist=[
                ('Content-Length', str(len(json_body))),
                ('Content-Type', 'application/json'),
            ],
            charset="utf-8"
        )

    def add_adapter(self, request: pyramid.request.Request, type_or_iface, adapter) -> None:
        self.json_renderer.add_adapter(type_or_iface, adapter)


def includeme(config: pyramid.config.Configurator) -> None:
    json_response = JsonResponse()
    config.add_directive('add_json_adapter', json_response.add_adapter)
    config.add_request_method(json_response.dump_json, name="dump_json")
    config.add_request_method(json_response.response_json, name="response_json")

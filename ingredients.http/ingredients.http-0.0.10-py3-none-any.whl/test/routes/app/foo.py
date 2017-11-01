import cherrypy

from ingredients_http.route import Route
from ingredients_http.router import Router
from ingredients_http.test.routes.app.validation_models.foo import RequestFooParams


class FooRouter(Router):
    def __init__(self):
        super().__init__(uri_base='foo')

    @Route(route="{foo_id}")
    @cherrypy.tools.model_params(cls=RequestFooParams)
    @cherrypy.tools.json_out()
    def get(self, foo_id):
        return {}

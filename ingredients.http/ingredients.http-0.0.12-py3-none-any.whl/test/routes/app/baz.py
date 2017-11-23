import cherrypy

from ingredients_http.route import Route
from ingredients_http.router import Router
from ingredients_http.test.routes.app.validation_models.baz import ResponseBaz


class BazRouter(Router):
    def __init__(self):
        super().__init__(uri_base='baz')

    @Route(route="bad")
    @cherrypy.tools.model_out(cls=ResponseBaz)
    def bad(self):
        response = ResponseBaz()
        return response

    @Route(route="good")
    @cherrypy.tools.model_out(cls=ResponseBaz)
    def good(self):
        response = ResponseBaz()
        response.foo = "bar"
        return response

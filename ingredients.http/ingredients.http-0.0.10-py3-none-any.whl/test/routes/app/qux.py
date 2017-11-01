import cherrypy

from ingredients_http.route import Route
from ingredients_http.router import Router
from ingredients_http.test.routes.app.validation_models.qux import ResponseQux


class QuxRouter(Router):
    def __init__(self):
        super().__init__(uri_base='qux')

    @Route(route="bad")
    @cherrypy.tools.model_out_pagination(cls=ResponseQux)
    def bad(self):
        response = ResponseQux()
        response.id = 1
        return [response], False

    @Route(route="good")
    @cherrypy.tools.model_out_pagination(cls=ResponseQux)
    def good(self):
        response = ResponseQux()
        response.id = 1
        response.foo = "bar"
        return [response], False

    @Route(route="page")
    @cherrypy.tools.model_out_pagination(cls=ResponseQux)
    def page(self):
        response = ResponseQux()
        response.id = 1
        response.foo = "bar"
        return [response], True

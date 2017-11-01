from tornado.web import RequestHandler, asynchronous, HTTPError
from tornado.httpclient import AsyncHTTPClient
from base.django_handler_mixin import DjangoHandlerMixin

ALLOWED_DOMAINS = {
    'search.gesis.org': True,
}


class Proxy(DjangoHandlerMixin, RequestHandler):
    @asynchronous
    def get(self, url):
        user = self.get_current_user()
        domain = url.split('/')[2]
        if domain not in ALLOWED_DOMAINS or not user.is_authenticated():
            self.set_status(401)
            self.finish()
            return
        query = self.request.query
        if query:
            url += '?' + query
        http = AsyncHTTPClient()
        http.fetch(
            url,
            method='GET',
            callback=self.on_response
        )

    # The response is asynchronous so that the getting of the data from the
    # remote server doesn't block the server connection.
    def on_response(self, response):
        if response.error:
            raise HTTPError(500)
        self.write(response.body)
        self.finish()

import falcon


class RedirectResource:
    """A simple redirect resource which can be used to force a route to
    redirect.

    :params path: the string version of the path to redirect to
    :params status: a falcon status object, default to falcon.HTTP_301
    """

    def __init__(self, path, status=None):
        self.path = path
        self.status = status or falcon.HTTP_301

    def on_get(self, req, resp):
        resp.status = self.status
        resp.set_header('Location', self.path)

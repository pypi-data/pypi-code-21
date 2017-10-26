from ahqapiclient.resources import Resource


class Noop(Resource):

    def __init__(self, http_client):
        super(Noop, self).__init__('/noop', http_client)

    def noop(self):
        return self.get(path=self.rurl())

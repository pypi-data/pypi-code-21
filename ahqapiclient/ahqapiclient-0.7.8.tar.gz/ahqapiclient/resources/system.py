from ahqapiclient.resources import Resource


class System(Resource):

    def __init__(self, http_client):
        super(System, self).__init__('/system', http_client)

    def expire_client_cooldown(self):
        return self.post(
            path=self.rurl('expire_client_cooldown')
        )

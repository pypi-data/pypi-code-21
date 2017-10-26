from ahqapiclient.resources import Resource


class BackendSettings(Resource):

    def __init__(self, http_client):
        super(BackendSettings, self).__init__('/settings/backend', http_client)

    def make_doc(self, settings, identifier):
        return {
            'settings': settings,
            'id': identifier
        }

    def update_settings(self, settings, identifier):
        return self.put(
            path=self.rurl(),
            data=self.make_doc(settings, identifier)
        )

    def get_settings(self, identifier):
        return self.get(path=self.rurl() + '/' + identifier)

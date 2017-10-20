from ahqapiclient.resources import Resource


class Settings(Resource):

    def __init__(self, http_client):
        super(Settings, self).__init__('/settings', http_client)

    def make_doc(self, settings):
        return {
            'settings': settings,
        }

    def create_settings(self, settings):
        return self.post(
            path=self.rurl(),
            data=self.make_doc(settings)
        )

    def update_settings(self, settings):
        return self.put(
            path=self.rurl(),
            data=self.make_doc(settings)
        )

    def get_settings(self):
        return self.get(path=self.rurl())

import stride

class Stride(stride.Stride):
    def __init__(self, app=None):
        self.app = app
        super().__init__(cloud_id=None, client_id=None, client_secret=None)
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.cloud_id = app.config['STRIDE_CLOUD_ID']
        self.client_id = app.config['STRIDE_CLIENT_ID']
        self.client_secret = app.config['STRIDE_CLIENT_SECRET']

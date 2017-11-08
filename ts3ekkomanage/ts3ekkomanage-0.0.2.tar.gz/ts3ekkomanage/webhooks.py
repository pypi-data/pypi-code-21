import bottle
import threading


class EkkoReverseClientContact:
    def __init__(self, ekkomanager, web_port=8180):
        self._app = bottle.Bottle()
        self._ekkomanager = ekkomanager
        self._routes()
        self._thread = threading.Thread(target=self._app.run, kwargs=dict(host='localhost', port=web_port))

    def _routes(self):
        self._app.route('/hello/<name>', callback=self.index)

        self._app.route('/command/spawn/<channel_id>', callback=self.spawn)
        self._app.route('/command/spawn/<channel_id>/<channel_password>', callback=self.spawn)
        self._app.route('/command/despawn/<channel_id>', callback=self.despawn)
        self._app.route('/command/register_move/<new_channel_id>', callback=self.despawn)

    def spawn(self, channel_id, channel_password=None):
        self._ekkomanager.spawn(channel_id, channel_password)

    def despawn(self, channel_id):
        pass

    def register_move(self, new_channel_id):
        pass

    def index(self, name):
        return bottle.template('<b>Hello {{name}}</b>!', name=name)

    def start(self):
        self._thread.start()

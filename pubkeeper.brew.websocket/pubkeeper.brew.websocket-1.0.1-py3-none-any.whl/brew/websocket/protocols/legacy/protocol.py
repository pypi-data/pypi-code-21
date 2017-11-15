import ujson as json
from pubkeeper.utils.logging import get_logger


class Protocol(object):
    def __init__(self):
        self.logger = get_logger("Brew legacy protocol")

    def on_connected(self, connection, topic):
        self._send_message(connection, 0, topic)

    def on_disconnected(self, connection, topic):
        self._send_message(connection, 1, topic)

    def brew(self, connection, brewer_id, topic, data):
        self._send_message(connection,
                           2, topic,
                           self.package_data(brewer_id, data))

    @staticmethod
    def unpackage_data(data):
        frame = json.loads(data)
        return frame['brewer_id'], frame['data']

    @staticmethod
    def package_data(brewer_id, data):
        return {
            'brewer_id': brewer_id,
            'data': data
        }

    def _send_message(self, connection, packet, topic, data=None):
        connection.write_message(json.dumps([
            packet,
            topic,
            data
        ]))

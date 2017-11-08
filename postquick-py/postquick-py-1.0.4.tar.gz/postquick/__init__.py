from socketIO_client_nexus import SocketIO

class PostQuick:
    socketIO = None

    def __init__(self, host, port, key):
        self.socketIO = SocketIO(
            host,
            port,
            params={'key': key}
        )
        self.socketIO.wait()

    def on(self, eventName, eventCallback):
        self.socketIO.on(eventName, eventCallback)

    def emit(self, eventName, eventValue):
        self.socketIO.emit(eventName, eventValue)

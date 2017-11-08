from socketIO_client_nexus import SocketIO

class PostQuick():
    socketIO = None

    def __init__(self, host, port, key):
        this.socketIO = SocketIO(
            host,
            port,
            params={'key': key}
        )
        this.socketIO.wait()

    def on(self, eventName, eventCallback):
        this.socketIO.on(eventName, eventCallback)

    def emit(self, eventName, eventValue):
        this.socketIO.emit(eventName, eventValue)

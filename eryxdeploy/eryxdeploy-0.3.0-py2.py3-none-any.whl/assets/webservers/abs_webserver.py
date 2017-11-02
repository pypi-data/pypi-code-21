class Webserver(object):
    def __init__(self, machine, webapp_name):
        self._machine = machine
        self._webapp_name = webapp_name

    def restart_server(self):
        raise NotImplementedError("Subclass responsibility.")

    def configure_server(self):
        raise NotImplementedError("Subclass responsibility.")

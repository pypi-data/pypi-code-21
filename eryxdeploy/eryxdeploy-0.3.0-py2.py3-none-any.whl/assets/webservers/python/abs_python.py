from eryx_deploy.assets.webservers.abs_webserver import Webserver


class PythonWebserver(Webserver):
    def __init__(self, machine, webapp_name, wsgi_package, virtual_env_path):
        super(PythonWebserver, self).__init__(machine=machine, webapp_name=webapp_name)
        self._wsgi_package = wsgi_package
        self._virtual_env_path = virtual_env_path

    def restart_server(self):
        raise NotImplementedError("Subclass responsibility.")

    def configure_server(self):
        raise NotImplementedError("Subclass responsibility.")

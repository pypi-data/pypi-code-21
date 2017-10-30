from eryx_deploy.assets.webservers.python.abs_python import PythonWebserver


class ApacheWithWSGIWebserver(PythonWebserver):
    """
    NOTE: Untested. Use with caution!
    """

    def restart_server(self):
        self._machine.run('sudo apache2ctl -k graceful')

    def configure_server(self):
        raise NotImplementedError("Not implemented yet! Please do it :)")

from eryx_deploy.assets.webservers.python.abs_python import PythonWebserver


class DjangoRunserverWebserver(PythonWebserver):
    """
    NOTE: Untested. Use with caution!
    """

    def restart_server(self):
        self._machine.run('python manage.py runserver')

    def configure_server(self):
        pass  # Nothing to configure

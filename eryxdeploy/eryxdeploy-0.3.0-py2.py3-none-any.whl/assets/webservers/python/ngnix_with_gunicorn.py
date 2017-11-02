import os

from eryx_deploy.assets.webservers.python.abs_python import PythonWebserver
from eryx_deploy.utils.interactive_console import InteractiveConsole


class NgnixWithGunicornWebserver(PythonWebserver):
    def restart_server(self):
        self._machine.run('sudo supervisorctl update')  # reload configuration updates
        self._machine.run('sudo service supervisor stop %s' % self._webapp_name)
        self._machine.run('sudo service supervisor start %s' % self._webapp_name)
        self._machine.run('sudo service nginx restart')

    def configure_server(self):
        self._machine.install_nginx()
        self._machine.install_supervisor()

        self._configure_nginx()
        self._configure_gunicorn()
        self._configure_supervisor()

    # configure nginx

    def _configure_nginx(self):
        if self._nginx_already_configured():
            InteractiveConsole.show_info("Nginx already configured for this project, skipping...")
            return

        config_file = '/etc/nginx/sites-available/%s' % self._webapp_name
        self._machine.run('sudo touch %s' % config_file)
        self._machine.append(config_file, self._nginx_project_configuration(), use_sudo=True)

        self._machine.run('sudo ln -s %s /etc/nginx/sites-enabled' % config_file)

    def _nginx_already_configured(self):
        config_file = '/etc/nginx/sites-available/%s' % self._webapp_name
        return self._machine.path_exists(config_file)

    def _nginx_project_configuration(self):
        configuration = 'upstream %s_server {\n' % self._webapp_name + \
                        '\tserver unix:%s/%s.sock;\n' % (
                            self._python_app_project_path(), self._webapp_name) + \
                        '}\n\n'

        configuration += 'server {\n' + \
                         '\tlisten 80;\n' + \
                         '\tserver_tokens off;\n' + \
                         '\tserver_name %s;\n\n' % self._machine.hostname() + \
                         '\tclient_max_body_size 100M;\n' + \
                         '\tlarge_client_header_buffers 4 8k;\n\n' + \
                         '\tlocation = /favicon.ico { access_log off; log_not_found off; }\n' + \
                         '\tlocation /static/ {\n' + \
                         '\t\troot %s;\n' % self._machine.project_path() + \
                         '\t}\n\n'

        configuration += '\tlocation / {\n' + \
                         '\t\t# include proxy_params;\n' + \
                         '\t\tproxy_redirect off;\n' + \
                         '\t\tproxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n' + \
                         '\t\tproxy_set_header Host $http_host;\n\n' + \
                         '\t\tproxy_read_timeout 1200s;\n' + \
                         '\t\tproxy_connect_timeout 1200s;\n\n' + \
                         '\t\tproxy_pass http://%s_server;\n' % self._webapp_name + \
                         '\t}\n' + \
                         '}'

        return configuration

    # gunicorn

    def _configure_gunicorn(self):
        if self._gunicorn_already_configured():
            InteractiveConsole.show_info("Gunicorn already configured for this project, skipping...")
            return

        with self._machine.cd(self._python_app_project_path()):
            self._machine.run('touch gunicorn_configuration.py')
            self._machine.append('gunicorn_configuration.py', self._gunicorn_project_configuration())

    def _gunicorn_already_configured(self):
        config_file = os.path.join(self._python_app_project_path(), 'gunicorn_configuration.py')
        return self._machine.path_exists(config_file)

    def _gunicorn_project_configuration(self):
        configuration = 'bind = \"unix:%s/%s.sock\"\n' % (self._python_app_project_path(), self._webapp_name)
        configuration += 'workers = 3\n'
        configuration += 'daemon = False\n'
        configuration += 'loglevel = "info"\n'
        configuration += 'errorlog = "/var/log/gunicorn_errors.log"\n'

        return configuration

    # supervisor

    def _configure_supervisor(self):
        if self._supervisor_already_configured():
            InteractiveConsole.show_info("Supervisor already configured for this project, skipping...")
            return

        config_file = '/etc/supervisor/conf.d/%s.conf' % self._webapp_name
        self._machine.run('sudo touch %s' % config_file)
        self._machine.append(config_file, self._supervisor_project_configuration(), use_sudo=True)

    def _supervisor_already_configured(self):
        config_file = '/etc/supervisor/conf.d/%s.conf' % self._webapp_name
        return self._machine.path_exists(config_file)

    def _supervisor_project_configuration(self):
        gunicorn_bin_path = os.path.join(self._virtual_env_path, 'bin/gunicorn')

        configuration = '[program:%s]\n' % self._webapp_name
        configuration += 'command=%s %s:application -c %s/gunicorn_configuration.py\n' % (
            gunicorn_bin_path, self._wsgi_package, self._python_app_project_path())
        configuration += 'directory=%s\n' % self._machine.project_path()
        configuration += 'autorestart=true\n'

        return configuration

    def _python_app_project_path(self):
        return os.path.join(self._machine.project_path(), self._webapp_name)

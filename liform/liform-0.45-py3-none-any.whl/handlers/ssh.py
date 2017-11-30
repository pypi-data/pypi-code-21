from .base import BaseHandler
from .base import BaseRefreshHandler
from ..utility import error_print


SERVER_TYPE_PATTERN = r"^\{[a-z]+\}server$"


class UploadRefreshHandler(BaseRefreshHandler):
    def _upload_directory(self, local_path, remote_path, variables):
        from jinja2 import FileSystemLoader
        from jinja2.sandbox import SandboxedEnvironment
        from os import lstat
        from os import readlink
        from os import walk
        from os.path import dirname
        from os.path import islink
        from os.path import join
        from stat import S_IMODE

        server_resource = self._resource.get_ancestor(SERVER_TYPE_PATTERN)
        ssh_client = server_resource._ssh_client

        for root, directories, files in walk(local_path):
            for directory in directories:
                directory_local_path = join(root, directory)
                directory_local_stat = lstat(directory_local_path)
                directory_remote_path = join(remote_path, root[len(local_path):], directory).replace('\\', '/')

                try:
                    ssh_client.lstat(directory_remote_path)
                except IOError:
                    ssh_client.mkdir(directory_remote_path, mode=directory_local_stat.st_mode)
                    ssh_client.chown(directory_remote_path, directory_local_stat.st_uid, directory_local_stat.st_gid)
                    ssh_client.chmod(directory_remote_path, S_IMODE(directory_local_stat.st_mode))
                    ssh_client.utime(directory_remote_path, (directory_local_stat.st_atime, directory_local_stat.st_mtime))

            for file in files:
                file_local_path = join(root, file)
                file_local_stat = lstat(file_local_path)

                if islink(file_local_path):
                    file_remote_path = join(remote_path + root[len(local_path):], file)

                    try:
                        ssh_client.remove(file_remote_path)
                    except IOError:
                        pass

                    self._out.write('\033[33;1mlink {0}\033[0m\n'.format(file_remote_path))
                    ssh_client.symlink(file_remote_path, readlink(file_local_path))
                else:
                    if file_local_path.endswith('.~remote'):
                        pass
                    elif file_local_path.endswith('.~'):
                        file_remote_path = join(remote_path, root[len(local_path):], file[:-2]).replace('\\', '/')

                        try:
                            with ssh_client.open(file_remote_path, 'r') as result_file:
                                old_content = result_file.read().decode(encoding='utf-8', errors='replace')

                            ssh_client.remove(file_remote_path)
                        except IOError:
                            old_content = ''

                        with open(file_local_path, 'r') as template_file:
                            template_code = template_file.read()

                        loader = FileSystemLoader(dirname(file_local_path))
                        environment = SandboxedEnvironment(
                            trim_blocks=False,
                            lstrip_blocks=False,
                            keep_trailing_newline=True,
                            autoescape=False,
                            loader=loader)
                        environment.globals.update(variables)

                        template_context = {
                            'old_content': old_content,
                            'this': self._resource.properties,
                            'server': server_resource.properties
                        }

                        for name, dependencies in self._resource.dependencies.items():
                            properties = []

                            for dependency in dependencies:
                                properties.append(dependency.properties)

                            template_context[name.replace('-', '_').replace('.', '_')] = properties

                        for name, dependencies in server_resource.dependencies.items():
                            properties = []

                            for dependency in dependencies:
                                properties.append(dependency.properties)

                            template_context[name.replace('-', '_').replace('.', '_')] = properties

                        template = environment.from_string(template_code)
                        result_text = template.render(template_context)

                        self._out.write('\033[33;1mmake {0}\033[0m\n'.format(file_remote_path))

                        with ssh_client.open(file_remote_path, 'w') as result_file:
                            result_file.write(result_text)
                    else:
                        file_remote_path = join(remote_path, root[len(local_path):], file).replace('\\', '/')

                        try:
                            ssh_client.remove(file_remote_path)
                        except IOError:
                            pass

                        self._out.write('\033[33;1mcopy {0}\033[0m\n'.format(file_remote_path))

                        ssh_client.put(file_local_path, file_remote_path)

                ssh_client.chown(file_remote_path, file_local_stat.st_uid, file_local_stat.st_gid)
                ssh_client.chmod(file_remote_path, S_IMODE(file_local_stat.st_mode))
                ssh_client.utime(file_remote_path, (file_local_stat.st_atime, file_local_stat.st_mtime))

    def fore_children(self, phase, settings, variables):
        from os.path import abspath
        from os.path import dirname
        from os.path import isdir
        from os.path import join
        from errno import ENOTDIR
        from os import strerror

        super().fore_children(phase, settings, variables)

        if self._resource.is_dirty:
            local_path = abspath(join(dirname(self._resource.source_file), self._resource.properties['local-path']))
            remote_path = self._resource.properties.get('remote-path', '/')
            ignore_missing = self._resource.properties.get('ignore-missing', '0').lower() in ('1', 'yes', 'true')

            if not isdir(local_path) and not ignore_missing:
                raise NotADirectoryError(ENOTDIR, strerror(ENOTDIR), local_path)

            self._upload_directory(local_path, remote_path, variables)


class UploadHandler(BaseHandler):
    def __init__(self, resource):
        super().__init__(UploadRefreshHandler, None, resource)

    def validate(self):
        if not 'local-path' in self._resource.properties:
            error_print(
                '{0}:{1} "ssh:upload" element requires "local-path" attribute.',
                self._resource.source_file,
                self._resource.source_line)


class ExecuteRefreshHandler(BaseRefreshHandler):
    def fore_children(self, phase, settings, variables):
        from time import sleep

        super().fore_children(phase, settings, variables)

        if self._resource.state == 0:
            server_resource = self._resource.get_ancestor(SERVER_TYPE_PATTERN)
            ssh_client = server_resource._ssh_client
            command = self._resource.properties['command']
            delay = float(self._resource.properties.get('delay', '0'))
            exit_status, stdout, stderr = ssh_client.execute(command)

            if exit_status == 0:
                text = '\033[32;1m{0}\033[0m = \033[30;1m{1}\033[0m\n'.format(exit_status, command)
            else:
                text = '\033[31;1m{0}\033[0m = \033[30;1m{1}\033[0m\n'.format(exit_status, command)

            if stderr:
                text += '\033[31;1m{0}\033[0m\n'.format(stderr)

            if stdout:
                text += '\033[32;1m{0}\033[0m\n'.format(stdout)

            self._out.write(text)
            sleep(delay)


class ExecuteHandler(BaseHandler):
    def __init__(self, resource):
        super().__init__(ExecuteRefreshHandler, None, resource)

    def validate(self):
        if not 'command' in self._resource.properties:
            error_print(
                '{0}:{1} "ssh:execute" element requires "local-path" attribute.',
                self._resource.source_file,
                self._resource.source_line)

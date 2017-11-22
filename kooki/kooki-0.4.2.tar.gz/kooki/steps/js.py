import os

from kooki.kooki import Kooki
from kooki.tools.output import Output
from kooki import DocumentException

from . import Step

class JsContent:

    def __init__(self):
        self.files = {}

    def __call__(self, *args):

        content = ''

        for arg in args:
            if arg in self.files:
                content += '<script>{0}</script>\n'.format(self.files[arg]())

        return content

    def add(self, name, js):
        self.files[name] = js

class Js(Step):

    def __init__(self, config):

        super().__init__(config)

        self._static = JsContent()
        self._infos = []
        self._name = 'js'
        self._config = config
        self._file_extension = '.js'

    def __call__(self):

        Output.start_step(self._name)

        for jar_path in self._config.jars:
            self._load_extensions(jar_path, self._file_extension)

        local_dir_path = os.path.join(os.getcwd(), 'kooki')
        self._load_extensions(local_dir_path, self._file_extension)

        Output.infos(self._infos, [('name', 'blue'), ('path', 'cyan')])

        return self._static

    def _load_extensions(self, directory, file_extension):

        if os.path.isdir(directory):
            self._load_extensions_rec(directory, file_extension)

    def _load_extensions_rec(self, directory, file_extension):

        for file_name in os.listdir(directory):

            if not os.path.isdir(os.path.join(directory, file_name)) and file_name.endswith(file_extension):

                extension_name = os.path.splitext(file_name)[0]
                path_to_extension = os.path.join(directory, file_name)

                kooki = Kooki(path_to_extension)
                parts = extension_name.split('.')
                self._static.add(extension_name, kooki)
                self._infos.append({'name': parts[-1], 'path': path_to_extension})

            else:

                sub_directory = os.path.join(directory, file_name)

                if os.path.isdir(sub_directory):

                    self._load_extensions_rec(sub_directory, file_extension)

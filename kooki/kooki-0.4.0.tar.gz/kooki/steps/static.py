import os

from kooki.kooki import Kooki
from kooki.tools.output import Output
from kooki import DocumentException

from . import Step

class Static(Step):

    def __init__(self, config):

        super().__init__(config)

        self._static = {}
        self._infos = []
        self._name = 'static'
        self._config = config

    def __call__(self, filters):

        Output.start_step(self._name)

        for file_extension in filters:

            for jar_path in self._config.jars:
                self._load_extensions(jar_path, file_extension)

            local_dir_path = os.path.join(os.getcwd(), 'kooki')
            self._load_extensions(local_dir_path, file_extension)

        Output.infos(self._infos, [('name', 'blue'), ('path', 'cyan')])

        return self._static

    def _load_extensions(self, directory, file_extension):

        if os.path.isdir(directory):
            self._load_extensions_rec(directory, file_extension)

    def _load_extensions_rec(self, directory, file_extension):

        for file in os.listdir(directory):

            if file.endswith(file_extension):

                extension_name = os.path.splitext(file)[0]
                path_to_extension = os.path.join(directory, file)

                kooki = Kooki(path_to_extension)

                parts = extension_name.split('.')
                current_level = self._static

                for part in parts[:-1]:

                    if part not in current_level:
                        current_level[part] = {}

                    current_level = current_level[part]

                current_level[parts[-1]] = kooki
                self._infos.append({'name': parts[-1], 'path': path_to_extension})

            else:

                sub_directory = os.path.join(directory, file)

                if os.path.isdir(sub_directory):

                    self._load_extensions_rec(sub_directory, file_extension)

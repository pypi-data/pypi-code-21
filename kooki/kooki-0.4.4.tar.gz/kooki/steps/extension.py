import os

from kooki.utensils import Empy, FrontMatter
from kooki.tools.output import Output
from kooki.kooki import Kooki

from . import Step

class Extension(Step):

    def __init__(self, config):

        super().__init__(config)

        self.extensions = {}
        self._infos = []
        self._name = 'extensions'
        self._config = config

        self._front_matter_recipe = FrontMatter()
        self._template_recipe = Empy()

    def __call__(self, filters):

        Output.start_step(self._name)

        for file_extension in filters:

            for package_dir_path in self._config.jars:
                self._load_extensions(package_dir_path, file_extension)

            local_dir_path = os.path.join(os.getcwd(), 'kooki')
            self._load_extensions(local_dir_path, file_extension)

        Output.infos(self._infos, [('name', 'blue'), ('path', 'cyan')])

        return self.extensions

    def _load_extensions(self, directory, file_extension):

        if os.path.isdir(directory):
            self._load_extensions_rec(directory, file_extension)

    def _load_extensions_rec(self, directory, file_extension):

        for file in os.listdir(directory):

            if file.endswith(file_extension):

                extension_name = os.path.splitext(file)[0]
                path_to_extension = os.path.join(directory, file)

                kooki = Kooki(path_to_extension)

                kooki.add_recipe(self._front_matter_recipe)
                kooki.add_recipe(self._template_recipe)

                parts = extension_name.split('.')
                current_level = self.extensions

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

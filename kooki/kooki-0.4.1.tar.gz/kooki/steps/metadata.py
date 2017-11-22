from kooki.kooki import Kooki
from kooki.tools.output import Output
from kooki.utensils import YamlMetadata, TomlMetadata, JsonMetadata
from kooki import DocumentException

import os

from . import Step

def data_merge(a, b):
    """merges b into a and return merged result

    NOTE: tuples and arbitrary objects are not handled as it is totally ambiguous what should happen"""

    class MergeError(Exception):
        pass

    key = None

    try:
        if a is None or isinstance(a, str) or isinstance(a, bytes) or isinstance(a, int) or isinstance(a, float):
            # border case for first run or if a is a primitive
            a = b
        elif isinstance(a, list):
            # lists can be only appended
            if isinstance(b, list):
                # merge lists
                a.extend(b)
            else:
                # append to list
                a.append(b)
        elif isinstance(a, dict):
            # dicts must be merged
            if isinstance(b, dict):
                for key in b:
                    if key in a:
                        a[key] = data_merge(a[key], b[key])
                    else:
                        a[key] = b[key]
            else:
                raise MergeError('Cannot merge non-dict "%s" into dict "%s"' % (b, a))
        else:
            raise MergeError('NOT IMPLEMENTED "%s" into "%s"' % (b, a))
    except TypeError as e:
        raise MergeError('TypeError "%s" in key "%s" when merging "%s" into "%s"' % (e, key, b, a))
    return a

class Metadata(Step):

    def __init__(self, config):

        super().__init__(config)

        self._infos = []
        self._name = 'metadata'
        self._config = config
        self.global_metadata = {}

    def __call__(self, metadata):

        metadata_dict = {}
        missing = False

        Output.start_step(self._name)

        for jar_path in self._config.jars:
            self._load_from_jars(jar_path, '.yaml')
            self._load_from_jars(jar_path, '.yml')
            self._load_from_jars(jar_path, '.toml')
            self._load_from_jars(jar_path, '.json')

        for source in metadata:

            try:
                if os.path.isfile(source):
                    path_to_source = os.path.join(os.getcwd(), source)
                elif source in self.global_metadata:
                    path_to_source = self.global_metadata[source]
                else:
                    raise Exception()

                kooki = self._load(path_to_source)

                kooki_cooked = kooki.cook()
                metadata_dict = data_merge(metadata_dict, kooki_cooked['metadata'])
                self._infos.append({'name': source, 'status': '[found]', 'path': path_to_source})
            except OSError:
                self._infos.append({'name': source, 'status': ('[missing]', 'red'), 'path': ''})
                missing = True

        if len(metadata) > 0:
            Output.infos(self._infos, [('name', 'cyan'), ('status', 'green'), ('path', 'cyan')])
        else:
            Output.info('no metadata')

        if missing:
            raise DocumentException('Missing files or sources')

        return metadata_dict

    def _load(self, source):

        kooki = Kooki(source)

        extension = kooki.extension()
        recipe = None

        if extension == '':
            recipe = self._guess_recipe(kooki.content())

        elif extension == 'yaml' or extension == 'yml':
            recipe = YamlMetadata()

        elif extension == 'toml':
            recipe = TomlMetadata()

        elif extension == 'json':
            recipe = JsonMetadata()

        if recipe is not None:
            kooki.add_recipe(recipe)

        return kooki

    def _load_from_jars(self, jars, filters):

        for package_dir_path in self._config.jars:
            self._load_metadata(package_dir_path, filters)

    def _load_metadata(self, directory, file_extension):

        if os.path.isdir(directory):
            self._load_metadata_rec(directory, file_extension)

    def _load_metadata_rec(self, directory, file_extension):

        for file in os.listdir(directory):

            if file.endswith(file_extension):

                extension_name = os.path.splitext(file)[0]
                path_to_extension = os.path.join(directory, file)
                self.global_metadata[file] = path_to_extension

            else:

                sub_directory = os.path.join(directory, file)

                if os.path.isdir(sub_directory):

                    self._load_metadata_rec(sub_directory, file_extension)

    def _guess_recipe(self, content):

        processors = []
        processors.append(YamlMetadata)
        processors.append(TomlMetadata)
        processors.append(JsonMetadata)

        succeed = False
        recipe = None

        while len(processors) > 0 and not succeed:
            try:
                Processor = processors.pop()
                recipe = Processor()
                succeed = True
            except:
                succeed = False

        return recipe

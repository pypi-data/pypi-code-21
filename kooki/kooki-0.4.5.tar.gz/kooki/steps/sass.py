import sass, os, shutil

from . import Step
from kooki.kooki import Kooki
from kooki.tools import read_file
from kooki.tools.output import Output

class SassContent:

    def __init__(self):
        self.files = {}

    def add(self, name, path):
        self.files[name] = path

    def __call__(self, name):

        processed_sass = ''
        current = os.getcwd()
        path = self.files[name]
        os.chdir(path)

        with open(os.path.join(path, name + '.scss')) as f:
            processed_sass = sass.compile(string=bytes(f.read(), 'utf8'))

        os.chdir(current)
        return '<style>{0}</style>'.format(processed_sass)

class Sass(Step):

    def __init__(self, config):

        super().__init__(config)

        self._sass = SassContent()
        self._infos = []
        self._name = 'sass'
        self._config = config

    def __call__(self):

        os.mkdir(os.path.join(self.temp_dir, 'sass'))

        def handler(path):

            sass_name = os.path.splitext(path)[0].split('/')[-1]
            shutil.copy(path, os.path.join(self.temp_dir, 'sass', sass_name + '.scss'))
            self._infos.append({'name': sass_name, 'path': path})
            self._sass.add(sass_name, os.path.join(self.temp_dir, 'sass'))
            return ''

        Output.start_step(self._name)

        for jar_path in self._config.jars:
            self.load_files_in_directory(handler, jar_path, '.scss')

        Output.infos(self._infos, [('name', 'blue'), ('path', 'cyan')])

        if Output.debug:
            pass
            # log_file = os.path.join(self.temp_dir, 'sass.css')
            # with open(log_file, 'w') as f:
            #     f.write(self._sass)
            # Output.info('Sass output: cat {0}'.format(log_file))

        return self._sass

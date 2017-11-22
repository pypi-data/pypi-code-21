import sass
import glob
import os
import base64
import em

from . import Step
from kooki.tools import read_file
from kooki.tools.output import Output

class FontContent:

    def __init__(self):
        self.fonts = {}

    def __call__(self, *args):

        content = ''

        if len(args) > 0:
            for arg in args:
                if arg in self.fonts:
                    content += '<style>{0}</style>\n'.format(self.fonts[arg]())

        else:
            for font in fonts:
                content += '<style>{0}</style>\n'.format(font)

        return content

    def add(self, name, font):
        self.fonts[name] = font


class Font(Step):

    font_types = ['black', 'extrabold', 'bold', 'semibold', 'regular', 'light', 'ultralight', 'hairline']
    font_weights = ['800', '700', '600', '500', '400', '300', '200', '100']

    otf_format = '''
@font-face
{
    font-family: \\font_name;
    src: url('data:font/opentype;base64, \\font_base64') format('opentype');
    font-weight: \\font_weight;
    font-style: normal;
}
'''

    def __init__(self, config):

        super().__init__(config)

        self._infos = []
        self._config = config
        self._name = 'fonts'

    def get(self):
        return Fonts(self.tex, self.html)

    def infos(self):
        return self._infos

    def __call__(self):

        Output.start_step(self._name)

        html = ''

        for jar_path in self._config.jars:

            content, files = self.load_files_in_directory(
                self.html_font_handler, jar_path, '.otf')
            html += content

            for font_file in files:
                self._infos.append({'name': font_file['path'], 'path': font_file['path']})

            content, files = self.load_files_in_directory(
                self.html_font_handler, jar_path, '.ttf')
            html += content

            for font_file in files:
                self._infos.append({'name': font_file['path'], 'path': font_file['path']})

        # Output.infos(self._infos, [('name', 'blue'), ('path', 'cyan')])

        return '<style>{0}</style>'.format(html)

    def html_font_handler(self, file):

        filename_with_ext = file.split('/')[-1]
        filename = filename_with_ext.split('.')[0]
        filename_strutured = filename.split('-')

        font_name = filename_strutured[0].lower()
        font_weight = '400'
        font_base64 = ''
        font_formatted = ''

        if len(filename_strutured) > 1:

            font_type_extracted = filename_strutured[1].lower()
            index = 0

            for font_type in self.font_types:

                if font_type == font_type_extracted:
                    font_weight = self.font_weights[index]
                    break

                if self.font_weights[index] == font_type_extracted:
                    font_weight = self.font_weights[index]
                    break

                index += 1

        with open(file, 'rb') as stream:

            content = stream.read()

            self._infos.append({'name': filename_with_ext, 'path': file})

            font_base64 = base64.b64encode(content)

            font_formatted = self.compile_font_to_otf(font_name, font_weight, str(font_base64.decode('utf8')))

        return font_formatted

    def compile_font_to_otf(self, font_name, font_weight, font_base64):

        data = {}
        data['font_name'] = font_name
        data['font_weight'] = font_weight
        data['font_base64'] = font_base64

        empy = em.Interpreter()
        empy.setPrefix('\\')
        font = empy.expand(self.otf_format, data)

        return font

    def tex_font_handler(self, file):

        filename_with_ext = file.split('/')[-1]
        filename = filename_with_ext.split('.')[0]
        font_formatted = ''

        with open(file, 'rb') as stream:

            content = stream.read()

            self._infos.append({'name': filename, 'path': ''})

            font_formatted = '\\newfontfamily\%s[]{%s}\n' % (filename.replace('-', ''), filename_with_ext)

        return font_formatted

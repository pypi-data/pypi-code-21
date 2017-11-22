from kooki.kooki import Kooki
from kooki.tools.output import Output
from kooki import DocumentException
from kooki.tools import read_file
from kooki.utensils import MarkdownToHTML, HTMLToTeX, Empy, FrontMatter
from xml.dom import minidom

from . import Step

class ContentKooki(Kooki):

    def __init__(self, content):

        self._content = content
        self._recipes = []

class Slides(Step):

    def __init__(self, config, tex=True):
        self._infos = []
        self._name = 'contents'
        self._tex = tex

    def __call__(self, files, metadata):

        content = ''
        missing = False

        Output.start_step(self._name)

        slide_number = 1

        for source in files:
            try:
                kookis = self._load(source, metadata)

                for kooki in kookis:
                    kooki_cooked = kooki.cook()

                    classes = ''
                    html_id = ''
                    others = ''
                    slide_content = kooki_cooked['content']

                    if kooki_cooked['content'].startswith('<p>{:'):
                        end = kooki_cooked['content'].find('}</p>')
                        attrs = kooki_cooked['content'][5:end].split()
                        slide_content = kooki_cooked['content'][end + 5:]

                        for attr in attrs:

                            if attr.startswith('.'):
                                classes += attr[1:]

                            elif attr.startswith('#'):
                                html_id = attr[1:]

                            else:
                                others += attr

                    content += '<section id="{0}" class="slide slide-{3} {1}" {2}>'.format(html_id, classes, others, slide_number)
                    content += '<div class="slide-number">{0}</div>'.format(slide_number)
                    content +=  '<div class="slide-content"><div class="slide-content-child">'
                    content += slide_content
                    content += '</div></div></section>'

                    slide_number += 1

                self._infos.append({'name': source, 'status': '[found]'})

            except Exception as e:
                print(e)
                self._infos.append({'name': source, 'status': ('[missing]', 'red')})
                missing = True

        if len(files) > 0:
            Output.infos(self._infos, [('name', 'cyan'), ('status', 'green')])
        else:
            Output.info('no content')

        if missing:
            raise DocumentException('Missing files ou sources')

        return content

    def _load(self, content_source, metadata):

        template = Empy(metadata)
        html = MarkdownToHTML()

        content = read_file(content_source)

        splitted = content.split('---\n')

        kookis = []

        for part in splitted:

            kooki = ContentKooki(part)
            kooki.add_recipe(template)
            kooki.add_recipe(html)

            kookis.append(kooki)

        return kookis

    def _get_image(image_path):
        image_file = urllib.urlopen(image_path)
        image_result = ''

        if image_file.code == 200:
            image_result = _convert_image(image_file)
        else:
            image_result = _get_local_image(image_path)

        image_db[str(image_path)] = image_result

        return image_result

    def _get_local_image(image_path):
        with open(image_path, "rb") as image_file:
            return _convert_image(image_file)

    def _convert_image(image_file):
        image_content_base64 = base64.b64encode(image_file.read())
        return 'data:image/png;base64,' + image_content_base64

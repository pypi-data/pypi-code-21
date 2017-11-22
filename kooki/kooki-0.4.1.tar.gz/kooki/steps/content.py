from kooki.kooki import Kooki
from kooki.tools.output import Output
from kooki import DocumentException

from kooki.utensils import MarkdownToHTML, HTMLToTeX, Empy, FrontMatter

from . import Step

class Content(Step):

    def __init__(self, config, tex=True):

        super().__init__(config)

        self._infos = []
        self._name = 'contents'
        self._tex = tex

    def __call__(self, files, metadata):

        content = ''
        missing = False

        Output.start_step(self._name)

        for source in files:
            try:
                kooki = self._load(source, metadata)
                kooki_cooked = kooki.cook()
                content += kooki_cooked['content']
                self._infos.append({'name': source, 'status': '[found]'})
            except DocumentException as e:
                raise DocumentException('{0}\n{1}'.format(source, e))
            except Exception as e:
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

        front_matter = FrontMatter()
        template = Empy(metadata)
        html = MarkdownToHTML()
        tex = HTMLToTeX()

        kooki = Kooki(content_source)

        kooki.add_recipe(front_matter)
        kooki.add_recipe(template)
        kooki.add_recipe(html)
        if self._tex:
            kooki.add_recipe(tex)

        return kooki

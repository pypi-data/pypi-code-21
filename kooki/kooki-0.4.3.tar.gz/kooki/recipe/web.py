from kooki.steps import Extension, Metadata, Document, Content, Sass, Font, Css, Js
from kooki.tools import write_file, DictAsMember

import em

def recipe(document, config):

    extension_step = Extension(config)
    extensions = extension_step(filters=['.html'])

    metadata_step = Metadata(config)
    metadata = metadata_step(metadata=document.metadata)

    font_step = Font(config)
    fonts = font_step()

    js_step = Js(config)
    js = js_step()

    css_step = Css(config)
    css = css_step()

    sass_step = Sass(config)
    sass = sass_step()

    content_step = Content(config, tex=False)
    content = content_step(files=document.contents, metadata={**extensions, **metadata})

    document_step = Document(config)
    document_content = document_step(template=document.template, extensions=extensions, metadata={
        **extensions,
        **metadata,
        'js': js,
        'css': css,
        'sass': sass,
        'fonts': fonts,
        'content': content})

    interpreter = em.Interpreter()
    interpreter.setPrefix('@')
    metadata_member = DictAsMember.convert(metadata)
    name = interpreter.expand(document.name, metadata_member)
    write_file(name + '.html', document_content)

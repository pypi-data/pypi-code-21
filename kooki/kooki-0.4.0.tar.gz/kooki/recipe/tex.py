from kooki.steps import Content, Extension, Metadata, Document, Xelatex
from kooki.tools import DictAsMember

import em

def recipe(document, config):

    extension_step = Extension(config)
    extensions = extension_step(filters=['.tex'])

    metadata_step = Metadata(config)
    metadata = metadata_step(metadata=document.metadata)

    content_step = Content(config)
    content = content_step(files=document.contents, metadata={**extensions, **metadata})

    document_step = Document(config)
    document_content = document_step(template=document.template, extensions=extensions, metadata={
        **extensions,
        **metadata,
        'content': content})

    interpreter = em.Interpreter()
    interpreter.setPrefix('@')
    metadata_member = DictAsMember.convert(metadata)
    name = interpreter.expand(document.name, metadata_member)

    xelatex_step = Xelatex(config)
    xelatex_step(name=name, document=document_content)

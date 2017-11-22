from kooki.steps import Extension, Metadata, Document
from kooki.tools import write_file, DictAsMember

import em

def recipe(document, config):

    extension_step = Extension(config)
    extensions = extension_step(filters=['.svg'])

    metadata_step = Metadata(config)
    metadata = metadata_step(metadata=document.metadata)

    document_step = Document(config)
    document_content = document_step(template=document.template, extensions=extensions, metadata={
        **extensions,
        **metadata})

    interpreter = em.Interpreter()
    interpreter.setPrefix('@')
    metadata_member = DictAsMember.convert(metadata)
    name = interpreter.expand(document.name, metadata_member)
    write_file(name + '.svg', document_content)

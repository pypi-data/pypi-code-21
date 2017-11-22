import os

class Document():

    def __init__(self, name, jars, template, contents, metadata, recipe):

        self.name = name
        self.jars = jars
        self.template = template
        self.contents = contents
        self.metadata = metadata
        self.recipe = recipe

        self.path = os.path.join(os.getcwd(), self.name)

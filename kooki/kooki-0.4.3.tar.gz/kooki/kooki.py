from kooki.tools import get_extension, read_file, write_file
from kooki.document_exception import DocumentException

import yaml

class Kooki():

    def __init__(self, source):

        try:
            self._content = read_file(source)
            self._extension = get_extension(source)

            self._recipes = []

        except FileNotFoundError as e:
            raise DocumentException('No such file: {0}'.format(source))

    def __call__(self, **kwargs):
        result = self.cook(**{'metadata': kwargs})
        return result['content']

    def cook(self, **kwargs):

        result = {'content': self._content}
        result.update(kwargs)

        for recipe in self._recipes:
            recipe_result = recipe(**result)
            result.update(recipe_result)

        return result

    def content(self):
        return self._content

    def extension(self):
        return self._extension

    def add_recipe(self, recipe):
        self._recipes.append(recipe)

    def remove_ustensil(self):
        self._recipes.pop()

import yaml
import toml
import json
from kooki import DocumentException
from . import Utensil

class YamlMetadata(Utensil):

    def __call__(self, **kwargs):

        if 'content' in kwargs:
            content = kwargs['content']
        else:
            raise DocumentException('YamlMetadata: argument error in step')

        yaml_content = yaml.load(content)
        if yaml_content == None:
            yaml_content = {}
        return {'metadata': yaml_content}

class TomlMetadata(Utensil):

    def __call__(self, **kwargs):

        if 'content' in kwargs:
            content = kwargs['content']
        else:
            raise DocumentException('TomlMetadata: argument error in step')

        return {'metadata': toml.loads(content)}

class JsonMetadata(Utensil):

    def __call__(self, **kwargs):

        if 'content' in kwargs:
            content = kwargs['content']
        else:
            raise DocumentException('JsonMetadata: argument error in step')

        return {'metadata': json.loads(content)}

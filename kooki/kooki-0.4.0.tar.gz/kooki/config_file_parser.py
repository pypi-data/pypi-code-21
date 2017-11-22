import time, os, yaml
import argparse

from . import Document, DocumentException
from kooki.tools.output import Output
from kooki.tools import read_file

class Config():

    def __init__(self):

        self.jars = []
        self.metadata = []
        self.content = []
        self.template = ''
        self.name = 'noname'
        self.recipe = []

    def __str__(self):
        return 'Config:\n{0}\n{1}\n{2}\n{3}\n{4}\n'.format(self.jars, self.metadata, self.content, self.template, self.name)

    def copy(self):

        config = Config()
        config.jars = self.jars.copy()
        config.metadata = self.metadata.copy()
        config.content = self.content.copy()
        config.template = self.template
        config.name = self.name
        config.recipe = self.recipe

        return config


def parse_args(args):

    documents = []

    if os.path.isfile(args.config_file):

        with open(args.config_file, 'r', encoding='utf8') as stream:

            config_raw = stream.read()
            config = yaml.load(config_raw)
            documents = parse_config(config)

            if args.documents != []:
                new_documents = {}

                for name in args.documents:
                    if name not in documents:
                        documents_availables = documents.keys()
                        documents_availables_str = '['
                        for key in list(documents_availables)[:-1]:
                            documents_availables_str += '\'' + key + '\', '
                        documents_availables_str += '\'' + list(documents_availables)[-1] + '\']'
                        raise DocumentException('No such rules for document: \'{0}\'\nRules availables {1}'.format(name, documents_availables_str))
                    else:
                        new_documents[name] = documents[name]
                documents = new_documents

    else:
        raise DocumentException('No such config file: {0}'.format(args.config_file))

    return documents


def parse_config(config_dict):

    documents = {}
    documents_config = {}

    config = Config()

    for key, value in config_dict.items():

        if key == 'template':
            config.template = value
        elif key == 'name':
            config.name = value
        elif key == 'recipe':
            parse_list('recipe', config.recipe, key, value)
        elif key == 'jars':
            parse_list('jars', config.jars, key, value)
        elif key == 'metadata':
            parse_list('metadata', config.metadata, key, value)
        elif key == 'content':
            parse_list('content', config.content, key, value)
        else:
            documents_config[key] = value
            config.name = key

    for document_key, document_args in documents_config.items():
        documents[document_key] = parse_document_config(document_args, config.copy())

    return documents


def parse_document_config(args, config):

    if isinstance(args, dict):

        for key, value in args.items():

            parse_list('jars', config.jars, key, value)
            parse_list('metadata', config.metadata, key, value)
            parse_list('content', config.content, key, value)
            parse_list('recipe', config.recipe, key, value)

            if 'template' == key: config.template = value
            if 'name' == key: config.name = value

    else:
        raise DocumentException('invalid kooki.yaml file')

    return Document(config.name, config.jars, config.template, config.content, config.metadata, config.recipe)


def parse_list(arg_key, arg_list, key, value):

    if arg_key == key and value is not None:
        if not isinstance(value, list):
            value = [value]
        arg_list += value
        return True
    else:
        return False


def parse_str(arg_key, arg, key, value):

    if arg_key == key:
        arg = value
        return True
    else:
        return False

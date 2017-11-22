from codecs import open

import requests
import em
import yaml
import os

def get_extension(filename):

    tmp = filename.split('.')

    if len(tmp) > 0:
        return tmp[-1]
    else:
        raise Exception('No extension')

def get_front_matter(content):

    first_line = content.split('\n', 1)[0]
    content_splitted = content.split('---\n')
    front_matter = {}

    if first_line == '---':

        if len(content_splitted) >= 3:
            metadata_content = content_splitted[1]
            content = '---\n'.join(content_splitted[2:])

            front_matter = yaml.load(metadata_content)
        else:
            content = '---\n'.join(content_splitted)

    return front_matter, content

def read_source(source):

    try:
        request = requests.get(source)
        content = request.text
        extension = ''

    except:
        content = read_file(source)

        split_source = source.split('.')
        extension = split_source[-1]

    return content, extension

def read_file(filename):

    content = ''

    with open(filename, 'r', encoding='utf8') as stream:
        content = stream.read()

    return content

def read_byte_file(filename):

    content = ''

    with open(filename, 'rb') as stream:
        content = stream.read()

    return content

def write_file(filename, content):

    elements = filename.split('/')
    path = ''
    for element in elements[:-1]:
        path = os.path.join(path, element)
        if path != '' and not os.path.isdir(path):
            os.mkdir(path)

    with open(filename, 'w', encoding='utf8') as stream:
        stream.write(content)

def deep_utf8(data):

    if isinstance(data, str):
        return data

    elif isinstance(data, list):
        new_data = []
        for value in data:
            new_data.append(deep_utf8(value))
        return new_data

    elif isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_data[key] = deep_utf8(value)
        return new_data

    else:
        return data


class DictAsMember(dict):

    @classmethod
    def convert(cls, data):

        if isinstance(data, dict):
            value = DictAsMember()
            for key in data:
                value[key] = DictAsMember.convert(data[key])
            return value
        else:
            return data

    def __getattr__(self, name):

        value = self[name]

        try:
            if isinstance(value, dict):
                value = DictAsMember(value)
            elif isinstance(value, unicode):
                data[key] = value.encode('utf8')
        except NameError:
            pass

        return value


class SafeEmpyInterpreter(em.Interpreter):

    def expand(self, content, data):

        result = ''
        missing = {}

        prefix = self.getPrefix()

        error = True
        new_data = DictAsMember(data)

        while error:
            try:
                result = super().expand(content, new_data)
                error = False
            except NameError as e:
                tag = str(e).split('\'')[1]
                new_data[tag] = DictAsMember()
                missing[tag] = ''
            except AttributeError as e:
                raise Exception('AttributeError: {0}'.format(str(e)))
            except TypeError as e:
                raise Exception('TypeError: {0}'.format(str(e)))
            except KeyError as e:
                raise Exception('KeyError: {0}'.format(str(e)))

        return result, missing


def format_data(data):

    for key, value in list(data.items()):

        try:
            if isinstance(value, dict):
                data[key] = DictAsMember(value)
            elif isinstance(value, unicode):
                data[key] = value.encode('utf8')
        except NameError:
            pass

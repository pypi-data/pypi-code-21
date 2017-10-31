import os

from zops.anatomy.text import dedent
from collections import OrderedDict


class UndefinedVariableInTemplate(KeyError):
    pass


class TemplateEngine(object):
    """
    Provide an easy and centralized way to change how we expand templates.
    """

    __singleton = None

    @classmethod
    def get(cls):
        if cls.__singleton is None:
            cls.__singleton = cls()
        return cls.__singleton

    def expand(self, text, variables):

        from jinja2 import Environment, Template, StrictUndefined
        env = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            undefined=StrictUndefined
        )

        def expandit(text_):
            text_ = str(text_)
            template_ = env.from_string(text_, template_class=Template)
            return template_.render(**variables)

        env.filters['expandit'] = expandit
        result = expandit(text)
        return result


class AnatomyFile(object):
    """
    Implements an abstraction of a file composed by blocks.

    Usage:
        f = AnatomyFile('filename.txt', 'first line')
        f.apply('directory')
    """

    def __init__(self, filename, contents, executable=False):
        self.__filename = filename
        self.__contents = dedent(contents)
        self.__executable = executable

    def apply(self, directory, variables, filename=None):
        """
        Create the file using all registered blocks.
        Expand variables in all blocks.

        :param directory:
        :param variables:
        :return:
        """
        expand = TemplateEngine.get().expand

        filename = filename or self.__filename
        filename = os.path.join(directory, filename)
        filename = expand(filename, variables)

        try:
            contents = expand(self.__contents, variables)
        except Exception as e:
            raise RuntimeError('ERROR: {}: {}'.format(filename, e))

        self._create_file(filename, contents)
        if self.__executable:
            self._make_executable(filename)

    @staticmethod
    def _create_file(filename, contents):

        contents = contents.rstrip('\n')
        contents += '\n'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        try:
            with open(filename, 'w') as oss:
                oss.write(contents)
        except Exception as e:
            raise RuntimeError(e)

    def _make_executable(self, path):
        mode = os.stat(path).st_mode
        mode |= (mode & 0o444) >> 2  # copy R bits to X
        os.chmod(path, mode)


class AnatomyTree(object):
    """
    A collection of anatomy-files.

    Usage:
        tree = AnatomyTree()
        tree.create_file('gitignore', '.gitignore', '.pyc')
        tree.apply('directory')
    """

    def __init__(self):
        self.__variables = OrderedDict()
        self.__files = {}

    def get_file(self, filename):
        """
        Returns a AnatomyFile instance associated with the given filename, creating one if there's none registered.

        :param str filename:
        :return AnatomyFile:
        """
        return self.__files.setdefault(filename, AnatomyFile(filename))

    def apply(self, directory, variables=None):
        """
        Create all registered files.

        :param str directory:
        :param dict variables:
        """
        dd = self.__variables.copy()
        if variables is not None:
            dd = merge_dict(dd, variables)

        for i_fileid, i_file in self.__files.items():
            try:
                filename = dd[i_fileid]['filename']
            except KeyError:
                filename = None
            i_file.apply(directory, variables=dd, filename=filename)

    def create_file(self, filename, contents, executable=False):
        """
        Create a new file in this tree.

        :param str filename:
        :param str contents:
        """
        if filename in self.__files:
            raise FileExistsError(filename)

        self.__files[filename] = AnatomyFile(filename, contents, executable=executable)

    def add_variables(self, variables, left_join=True):
        """
        Adds the given variables to this tree variables.

        :param dict variables:
        :param bool left_join:
            If True, the root keys of the new variables (variables parameters) must already exist in the current
            variables dictionary.
        """
        self.__variables = merge_dict(self.__variables, variables, left_join=left_join)


def merge_dict(d1, d2, left_join=True):
    """

    :param dict d1:
    :param dict d2:
    :return:
    """
    return _merge_dict(d1, d2, depth=0, left_join=left_join)


def _merge_dict(d1, d2, depth=0, left_join=True):

    def merge_value(v1, v2):
        if v2 is None:
            return v1
        elif isinstance(v1, dict):
            return _merge_dict(v1, v2, depth=depth+1, left_join=left_join)
        elif isinstance(v1, (list, tuple)):
            return v1 + v2
        else:
            return v2

    if left_join and depth < 2:
        keys = d1.keys()
        right_keys = set(d2.keys()).difference(set(d1.keys()))
        if right_keys:
            raise RuntimeError('Extra keys: {}'.format(right_keys))
    else:
        keys = list(d1.keys()) + [i for i in d2.keys() if i not in d1]

    result = OrderedDict()
    for i_key in keys:
        result[i_key] = merge_value(d1.get(i_key), d2.get(i_key))
    return result

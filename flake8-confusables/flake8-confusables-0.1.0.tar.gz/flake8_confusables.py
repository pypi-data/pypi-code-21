import io
import tokenize

import confusables
import pycodestyle

__version__ = '0.1.0'

__all__ = ('IdentifierChecker',)


class ConfusableError(Exception):
    code = 'C001'

    def __init__(self, start, current, previous):
        self.lineno, self.column = start
        self.current = current
        self.previous = previous

    @property
    def short_desc(self):
        return "ambiguous identifier found ('{0}' matches '{1}')".format(
            self.current, self.previous)


class IdentifierChecker(object):
    name = 'flake8-confusables'
    version = __version__

    def __init__(self, tree, filename=None):
        self.filename = filename
        self.load_file()

    def check_identifiers(self):
        identifiers = {}

        gen = tokenize.generate_tokens(io.StringIO(self.lines).readline)
        for token in gen:
            skeleton = confusables.skeleton(token.string)
            confused = identifiers.get(skeleton)
            if confused is not None and token.string != confused.string:
                yield ConfusableError(
                    token.start, token.string, confused.string)
            identifiers[skeleton] = token

    def load_file(self):
        if self.filename in ('stdin', '-', None):
            self.filename = 'stdin'
            self.lines = pycodestyle.stdin_get_value().splitlines(True)
        else:
            with tokenize.open(self.filename) as f:
                self.lines = f.read()

    def run(self):
        for error in self.check_identifiers():
            message = '{0} {1}'.format(error.code, error.short_desc)
            yield error.lineno, error.column, message, type(error)

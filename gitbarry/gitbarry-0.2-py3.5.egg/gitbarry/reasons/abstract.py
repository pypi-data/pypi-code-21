import sys


class AbstractReason:
    args = []

    def __init__(self, *args):
        self.args = args or []
        if len(self.args) and 'help' in self.args:
            self.usage()
            sys.exit(0)

    def usage(self):
        """
        Print usage text
        """
        raise NotImplementedError

    def validate(self) -> []:
        raise NotImplementedError

    def run(self) -> int:
        raise NotImplementedError

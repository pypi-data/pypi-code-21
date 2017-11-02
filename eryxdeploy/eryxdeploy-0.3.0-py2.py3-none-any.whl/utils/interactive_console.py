from fabric.colors import red, yellow, green
from fabric.contrib.console import confirm
from fabric.utils import abort, puts


class InteractiveConsole(object):
    @staticmethod
    def yes_or_no(question, default=True):
        return confirm(green(question), default=default)

    @staticmethod
    def abort(message=None):
        if not message:
            message = "Aborting."
        abort(red(message))

    @staticmethod
    def abort_with_suggestion(message):
        abort(yellow(message))

    @staticmethod
    def show_info(message):
        puts(yellow(message))

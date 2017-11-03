import webbrowser
from gitbarry.utils import git
from .abstract import AbstractAction


class Action(AbstractAction):
    def init(self):
        self.current_branch = git.get_current_branch()
        print("Opening broser at %s" % self.current_branch)

    def run(self):
        url = self.params['finish-open-browser-url'].format(branch = self.current_branch)
        webbrowser.open_new_tab(url)


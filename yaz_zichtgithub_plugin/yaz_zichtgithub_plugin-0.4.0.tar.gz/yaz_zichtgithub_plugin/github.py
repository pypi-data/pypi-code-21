import github
import yaz

__all__ = ["Github"]


class Github(yaz.BasePlugin):
    token = None

    def __init__(self):
        if not (self.token):
            raise RuntimeError("The personal access token must be specified, please add a Github plugin override in your user directory")

        self.service = github.Github(self.token)

    def get_service(self):
        return self.service

import requests
from gitbarry.utils import git
from .abstract import AbstractAction


class Action(AbstractAction):
    def init(self):
        print("Creating pull-request to %s" % self.params['finish-branch'])

    def send_pull_request(self):
        to_branch = self.params['finish-branch']
        method = self.params.get('finish-pull-request-method', 'get').lower()
        url = self.params['finish-pull-request-url'].format(branch =  to_branch)
        print("%s %s..." % (method.upper(), url), end=' ')
        resp = getattr(requests, method)(url)
        print(resp.status_code)

    def run(self):
        self.send_pull_request()

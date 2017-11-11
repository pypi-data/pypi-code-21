class Commit:

    def __init__(self, message):
        self.message = message

    def parse(self):
        pass

    def validate(self, regex):
        pass

    def is_valid(self):
        pass


class Changelog:

    def parse(self):
        pass

    def last_version(self):
        pass


class BaseChangelog:

    changelog = Changelog()

    @property
    def regex(self):
        pass

    def commits_logs(self, last_version, everything):
        [Commit(msg)]

    def last_generated(self):
        pass

    def generate(self, everything=False):
        last_version = self.changelog.last_version()
        commits = self.commits_logs(last_version, everything)


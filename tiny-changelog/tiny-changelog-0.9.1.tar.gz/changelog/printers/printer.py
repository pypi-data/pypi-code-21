import io

from ..timeline import Tag, PullRequest, UnreleasedTag


class Printer(object):
    def __init__(self, timeline, start_at=None, with_unreleased=False):
        self.timeline = timeline
        self.start_at = start_at
        self.with_unreleased = with_unreleased

    def _walk_timeline(self):
        pull_requests = []
        for event in self.timeline.events:
            if isinstance(event, PullRequest):
                pull_requests.insert(0, event)

            if isinstance(event, Tag):
                yield event, pull_requests
                pull_requests = []

        if self.with_unreleased and pull_requests:
            yield UnreleasedTag, pull_requests

    def iteritems(self):
        items = reversed([item for item in self._walk_timeline()])
        for tag, pull_requests in items:
            yield tag, pull_requests

    def print_to_file(self, filename):
        with io.open(filename, 'w', encoding='utf-8') as f:
            for line in self.iteritems():
                if isinstance(line, str):
                    line = line.decode('utf-8')
                f.write(line)

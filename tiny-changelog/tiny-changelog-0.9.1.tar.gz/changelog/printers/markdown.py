from .printer import Printer


class MarkdownPrinter(Printer):
    def header(self):
        return u'# Change Log'

    def footer(self):
        return u''

    def break_line(self):
        return u'\n'

    def tag_line(self, tag):
        return u'# [{name}]({url})'.format(**tag.as_dict)

    def pull_request_line(self, pr):
        author_url = self.timeline.feed.user_url(pr.author)
        return (
            u'* [\#{number}]({url}) {title} [@{author}]({author_url})'.format(
                author_url=author_url, **pr.as_dict
            )
        )

    def no_pull_requests_seen_line(self, all_tags, tag):
        try:
            next_tag = all_tags[all_tags.index(tag) + 1]
        except IndexError:
            next_tag = tag

        url = self.timeline.feed.compare_url(next_tag.name, tag.name)
        return (
            u'No pull requests merged for this version, '
            u'see [commit history]({url})'
        ).format(url=url)

    def list_all_tags(self):
        return [tag for tag, _ in super(MarkdownPrinter, self).iteritems()]

    def iteritems(self):
        all_tags = self.list_all_tags()

        yield self.header()
        yield self.break_line()
        yield self.break_line()

        for tag, pull_requests in super(MarkdownPrinter, self).iteritems():
            yield self.tag_line(tag)
            yield self.break_line()

            if not pull_requests:
                yield self.no_pull_requests_seen_line(all_tags, tag)
                yield self.break_line()

            for pr in pull_requests:
                yield self.pull_request_line(pr)
                yield self.break_line()

            yield self.break_line()

        yield self.footer()

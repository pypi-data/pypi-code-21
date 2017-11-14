"""
Classes to represent a blog.
"""

import datetime

import attr


@attr.s(frozen=True)
class Post(object):
    """
    A blog post
    """
    title = attr.ib()
    slug = attr.ib()
    date = attr.ib()
    author = attr.ib()
    contents = attr.ib()

    @property
    def formatted_date(self):
        """
        Human-readable data string.
        """
        when = datetime.datetime.strptime(self.date, "%Y-%m-%d %H:%M")
        return when.strftime('%c')

    @property
    def rel_link(self):
        """
        Link to post.
        """
        return self.slug + '.html'


@attr.s(frozen=True)
class Page(object):
    """
    A page (non-time-dependant content)
    """
    title = attr.ib()
    slug = attr.ib()
    author = attr.ib()
    contents = attr.ib()

    formatted_date = ""

    @property
    def rel_link(self):
        """
        Link to page.
        """
        return self.slug + '.html'


@attr.s(frozen=True)
class Metadata(object):
    """
    Blog metadata
    """
    title = attr.ib()
    description = attr.ib()
    links = attr.ib(default=attr.Factory(list))


@attr.s(frozen=True)
class Blog(object):
    """
    A blog
    """
    metadata = attr.ib()
    posts = attr.ib()
    pages = attr.ib()

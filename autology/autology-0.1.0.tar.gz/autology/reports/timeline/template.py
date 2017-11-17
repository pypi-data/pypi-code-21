"""Simple template definition for a log file that contains start time, end time, location, and empty content."""
from datetime import datetime

import frontmatter

from autology.reports.models import Template


def register_template():
    return Template('timeline_base', template_start, template_end)


def template_start():
    """ Start a new file template based on the content of the template definition. """

    _post = frontmatter.Post('',
                             time=datetime.now(),
                             end_time=None,
                             location='home')
    return _post


def template_end(post):
    """
    Finish the manipulation of the metadata in the front matter before saving the contents to the storage engine.
    :param post: the post file that will be modified.
    """
    if not post.metadata['end_time']:
        post.metadata['end_time'] = datetime.now()

    return post

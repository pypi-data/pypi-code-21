"""
@file
@brief About templates.
"""
import os


def get_template(name):
    """
    Get a template name.

    @param      name    template name
    @return             content
    """
    this = os.path.dirname(name)
    tm = os.path.join(this, name)
    if not os.path.exists(tm):
        raise FileNotFoundError("Unable to find template '{0}'.".format(name))
    with open(tm, "r", encoding="utf-8") as f:
        return f.read()

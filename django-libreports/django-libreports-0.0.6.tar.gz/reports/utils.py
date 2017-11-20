import os
from random import choice
from string import ascii_uppercase, ascii_lowercase, digits

from django.template.defaultfilters import slugify


def hashed_upload_to(prefix, fileattr, filename):
    """
    Helper for Django FileField upload_to. It creates a path that consists
    of a prefix a random string and the filename.
    """

    base, ext = os.path.splitext(filename)
    options = ascii_uppercase + ascii_lowercase + digits
    rand = ''.join(choice(options) for _ in range(10))
    return '%s/%s/%s%s' % (prefix, rand, slugify(base), ext)

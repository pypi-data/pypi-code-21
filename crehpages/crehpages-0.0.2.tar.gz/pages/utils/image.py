import os
import uuid

from imagekit.processors import ResizeToFill

from django.utils import timezone


def get_slider_sizes(sizes):
    slider_sizes = []
    slider_sizes.append(ResizeToFill(width=sizes[0], height=sizes[1]))
    return slider_sizes


def upload_picture_to(obj, filename):
    f, ext = os.path.splitext(filename)
    _uuid = str(uuid.uuid4()).replace('-', '')
    url = 'pages/slider/%(date_now)s/%(uuid)s%(ext)s' % {
        'date_now': timezone.now().strftime('%Y/%m/%d'),
        'uuid': _uuid,
        'ext': ext
    }
    return url
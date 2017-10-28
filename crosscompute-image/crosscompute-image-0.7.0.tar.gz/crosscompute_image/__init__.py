from crosscompute.scripts.serve import get_result_file_url, import_upload_from
from crosscompute.types import DataType
from invisibleroads_macros.disk import link_path


class ImageType(DataType):
    suffixes = 'image',
    formats = 'jpg', 'png', 'gif'
    template = 'crosscompute_image:type.jinja2'
    views = [
        'import_image',
    ]

    @classmethod
    def load(Class, path):
        # Check that we can load the image
        return path

    @classmethod
    def save(Class, path, value):
        link_path(path, value)

    @classmethod
    def render(Class, value):
        return get_result_file_url(value)


def import_image(request):
    return import_upload_from(request, ImageType, {})

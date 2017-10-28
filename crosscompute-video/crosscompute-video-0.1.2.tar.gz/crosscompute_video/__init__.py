from crosscompute.scripts.serve import get_result_file_url
from crosscompute.types import DataType


class VideoType(DataType):

    suffixes = 'video',
    formats = 'mp4', 'wav'
    template = 'crosscompute_video:type.jinja2'

    @classmethod
    def load(Class, path):
        return path

    @classmethod
    def render(Class, path):
        return get_result_file_url(path)

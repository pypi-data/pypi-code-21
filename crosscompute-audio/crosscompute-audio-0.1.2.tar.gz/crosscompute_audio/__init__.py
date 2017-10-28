from crosscompute.scripts.serve import get_result_file_url
from crosscompute.types import DataType


class AudioType(DataType):

    suffixes = 'audio',
    formats = 'mp3', 'ogg'
    template = 'crosscompute_audio:type.jinja2'

    @classmethod
    def load(Class, path):
        return path

    @classmethod
    def render(Class, path):
        return get_result_file_url(path)

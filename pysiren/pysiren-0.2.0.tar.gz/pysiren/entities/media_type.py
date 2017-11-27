from ..renderer import RendererMixin
from ..error import SirenMediaTypeError
import re

_media_type_pattern = re.compile(
    """^(application|audio|image|message|model|multipart|text|video)\\/([A-Z]|[a-z]|[0-9]|[\\!\\#\\$\\&\\.\\+\\-\\^\\_]){1,127}(; ?(([\\!\\#\\$\\%\\&\\'\\(\\)\\*\\+-\\.\\/]|[0-9]|[A-Z]|[\\^\\_\\`\\]\\|]|[a-z]|[\\|\\~])+)+=((([\\!\\#\\$\\%\\&\\'\\(\\)\\*\\+-\\.\\/]|[0-9]|[A-Z]|[\\^\\_\\`\\]\\|]|[a-z]|[\\|\\~])+)|\"([\\!\\#\\$\\%\\&\\.\\(\\)\\*\\+\\,\\-\\.\\/]|[0-9]|[\\:\\;\\<\\=\\>\\?\\@]|[A-Z]|[\\[\\\\\\]\\^\\_\\`]|[a-z]|[\\{\\|\\}\\~])+\"))*$""")


class SirenMediaType(RendererMixin):
    def __init__(self, type):
        if _media_type_pattern.match(type) is None:
            raise SirenMediaTypeError("Invalid Media Type [%s]", type)

        self._type = type

    @property
    def data(self):
        return self._type


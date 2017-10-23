from urllib.parse import urljoin

# API_ROOT = 'http://trunity.mkechinov.ru/api/v3/'  # STAGE environment
API_ROOT = 'http://trunity.org/api/v3/'         # PROD environment
URL_DETAIL_PREFIX = '{id}'


class Url(object):

    def __init__(self, root: str) -> None:
        self._root = root + '/' if not root.endswith('/') else root
        self._tail = None
        self._detail_prefix = URL_DETAIL_PREFIX

        self._url_list = None
        self._url_detail = None

    @property
    def tail(self):
        if not self._tail:
            raise NotImplementedError(
                'Url tail is not set!'
            )
        else:
            return self._tail

    @tail.setter
    def tail(self, value: str):
        self._tail = value

    @property
    def list(self) -> str:
        return urljoin(self._root, self.tail)

    @property
    def detail(self) -> str:
        return urljoin(self.list + '/', self._detail_prefix)

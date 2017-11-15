# coding=utf-8
from ..connection_mixin import ConnectionMixin
from ..dulwich.refs import RefsContainer


SYMREF = b'ref: '


class SpannerRefContainer(RefsContainer, ConnectionMixin):
    def __init__(self, connection):
        super(SpannerRefContainer, self).__init__()
        self._create_table_if_needed()

    def get_packed_refs(self):
        return {}

    def read_loose_ref(self, name):
        raise NotImplementedError(self.read_loose_ref)

    def set_if_equals(self, name, old_ref, new_ref):
        raise NotImplementedError(self.set_if_equals)

    def add_if_new(self, name, ref):
        raise NotImplementedError(self.add_if_new)

    def remove_if_equals(self, name, old_ref):
        raise NotImplementedError(self.remove_if_equals)

    def _create_connection(self, **kwargs):
        raise NotImplementedError(self._create_connection)

    def _create_table_if_needed(self):
        raise NotImplementedError(self._create_table_if_needed)

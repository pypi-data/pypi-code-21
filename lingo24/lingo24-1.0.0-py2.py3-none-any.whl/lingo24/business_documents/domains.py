from .collections import SortablePaginatableAddressableCollection


class DomainCollection(SortablePaginatableAddressableCollection):
    url_path = 'domains/'

    def make_item(self, **kwargs):
        return Domain(
            domain_id=kwargs['id'],
            name=kwargs['name'],
            )


class Domain(object):
    def __init__(self, domain_id, name):
        self.id = domain_id
        self.name = name

    def __repr__(self):
        return '<Domain {}: {}>'.format(self.id, self.name)

    def __eq__(self, other):
        return all((
            self.id == other.id,
            self.name == other.name,
            ))

    def __ne__(self, other):
        return not self.__eq__(other)

from .collections import SortablePaginatableAddressableCollection


class ServiceCollection(SortablePaginatableAddressableCollection):
    url_path = 'services/'

    def make_item(self, **kwargs):
        return Service(
            service_id=kwargs['id'],
            name=kwargs['name'],
            description=kwargs['description'],
            )


class Service(object):
    def __init__(self, service_id, name, description):
        self.id = service_id
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Service {}: {}>'.format(self.id, self.name)

    def __eq__(self, other):
        return all((
            self.id == other.id,
            self.name == other.name,
            self.description == other.description,
            ))

    def __ne__(self, other):
        return not self.__eq__(other)

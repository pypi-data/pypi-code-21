from .collections import SortablePaginatableAddressableCollection


class LocaleCollection(SortablePaginatableAddressableCollection):
    url_path = 'locales/'

    def make_item(self, **kwargs):
        return Locale(
            locale_id=kwargs['id'],
            name=kwargs['name'],
            language=kwargs['language'],
            country=kwargs['country'],
            )


class Locale(object):
    def __init__(self, locale_id, name, language, country):
        self.id = locale_id
        self.name = name
        self.language = language
        self.country = country

    def __repr__(self):
        return '<Locale {}: {}>'.format(self.id, self.name)

    def __eq__(self, other):
        return all((
            self.id == other.id,
            self.name == other.name,
            self.language == other.language,
            self.country == other.country,
            ))

    def __ne__(self, other):
        return not self.__eq__(other)

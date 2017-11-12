from threading import Lock


def error_print(text, *args, **kwargs):
    from sys import exit
    from sys import stderr

    print(text.format(*args, **kwargs), file=stderr)
    exit(1)


def warning_print(text, *args, **kwargs):
    from sys import stderr

    print(text.format(*args, **kwargs), file=stderr)


class PathDict(object):
    def __init__(self, parent=None):
        from collections import OrderedDict

        self.parent = parent
        self._items = OrderedDict()

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        for key in self._items:
            item = self._items[key]

            if isinstance(item, PathDict):
                for inner_key in item:
                    yield key + '.' + inner_key
            else:
                yield key

    def __contains__(self, item):
        return item in self._items

    def __missing__(self, item):
        return not item in self._items

    def __getitem__(self, key, **kwargs):
        if (key is None) or (key == ''):
            return self

        if not isinstance(key, str):
            raise KeyError('key must be string')

        parts = key.split('.')
        prev_path_dict = self
        next_path_dict = self

        for index in range(0, len(parts) - 1):
            if parts[index] in prev_path_dict._items:
                next_path_dict = prev_path_dict._items[parts[index]]

                if not isinstance(next_path_dict, PathDict):
                    next_path_dict = PathDict(prev_path_dict)
                    prev_path_dict._items[parts[index]] = next_path_dict
            else:
                next_path_dict = PathDict(prev_path_dict)
                prev_path_dict._items[parts[index]] = next_path_dict

            prev_path_dict = next_path_dict
            next_path_dict = None

        if parts[len(parts) - 1] in prev_path_dict._items:
            return prev_path_dict._items[parts[len(parts) - 1]]

        next_path_dict = PathDict(prev_path_dict)
        prev_path_dict._items[parts[len(parts) - 1]] = next_path_dict

        return next_path_dict

    def __setitem__(self, key, value, **kwargs):
        if not isinstance(key, str):
            raise KeyError('key must be string')

        parts = key.split('.')
        prev_path_dict = self
        next_path_dict = self

        for index in range(0, len(parts) - 1):
            if parts[index] in prev_path_dict._items:
                next_path_dict = prev_path_dict._items[parts[index]]

                if not isinstance(next_path_dict, PathDict):
                    next_path_dict = PathDict(prev_path_dict)
                    prev_path_dict._items[parts[index]] = next_path_dict
            else:
                next_path_dict = PathDict(prev_path_dict)
                prev_path_dict._items[parts[index]] = next_path_dict

            prev_path_dict = next_path_dict
            next_path_dict = None

        prev_path_dict._items[parts[len(parts) - 1]] = value

        return value

    def keys(self):
        return self._items.keys()

    def items(self):
        return self._items.items()

    def dump(self):
        from collections import OrderedDict

        result = OrderedDict()

        for key in self._items.keys():
            item = self._items[key]

            if isinstance(item, PathDict):
                result[key] = item.dump()
            else:
                result[key] = item

        return result

    def __dump_flat(self, result, path, items):
        for key in items.keys():
            item = items[key]
            item_path = key if path is None else '{0}.{1}'.format(path, key)

            if isinstance(item, PathDict):
                self.__dump_flat(result, item_path, item._items)
            else:
                result[item_path] = item

    def dump_flat(self):
        from collections import OrderedDict

        result = OrderedDict()

        self.__dump_flat(result, None, self._items)

        return result

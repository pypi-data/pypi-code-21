from uuid import uuid4
from collections import defaultdict


class Laminated:
    def __init__(self):
        self._union_data = dict()
        self._layers_names = []
        self._map_layers_to_keys = defaultdict(list)

        self._data = defaultdict(dict)

    def __getitem__(self, item):
        return self._union_data[item]

    def __iter__(self):
        return iter(self._union_data.keys())

    def add_layer(self, data, name=None):
        if name is None:
            name = uuid4().hex

        if name in self._layers_names:
            raise ValueError('Duplicate layers names')

        self._layers_names.insert(0, name)
        self._union_data.update(data)

        for k, v in data.items():
            self._data[k][name] = v
            self._map_layers_to_keys[name].append(k)

    def get_layers_names(self):
        for name in self._layers_names:
            yield name

    def get_value_at_layer(self, layer_name, key):
        start_search = False

        for current_layer_name in self._layers_names:
            if current_layer_name == layer_name:
                start_search = True
            if not start_search:
                continue

            if current_layer_name in self._data[key]:
                return self._data[key][current_layer_name]
        else:
            raise KeyError('{!r} not in dict'.format(key))

    def get_dict_at_layer(self, name):
        if name not in self._layers_names:
            raise ValueError('Layer {!r} not exists')

        result = {}
        for layer_name in reversed(self._layers_names):
            for key in self._map_layers_to_keys[layer_name]:
                result[key] = self._data[key][layer_name]

            if layer_name == name:
                return result



class KeysNav(object):
    def __init__(self, items, offset=None, show_N_objs=None, back_string='Назад', show_back=True):
        if show_back and back_string is None:
            raise ValueError('If show_back is True, back_string can\'t be None')

        self.items = items
        self.offset = 0 if not offset else offset
        self.show_N_dirs = 3 if not show_N_objs else show_N_objs
        self.show_back = show_back
        self.back_string = back_string
        if isinstance(self.items, dict):
            self.keys = list(self.items.keys())
        else:
            self.keys = self.items

    def get_real_keys(self):
        return self.keys

    def get_keys(self):
        keys = None
        if self.offset + self.show_N_dirs >= len(self.keys):
            keys = [[key] for key in self.keys[self.offset:]]
        else:
            keys = [[key] for key in self.keys[self.offset:self.offset + self.show_N_dirs]]
        last_row = []
        if self.offset > 0:
            last_row.append('<<')

        if self.show_back:
            last_row.append(self.back_string)

        if self.offset + self.show_N_dirs < len(self.keys):
            last_row.append('>>')
        keys.append(last_row)
        return keys

    def backward(self):
        self.offset = max(self.offset - self.show_N_dirs, 0)
        return self.get_keys()

    def forward(self):
        self.offset += self.show_N_dirs
        return self.get_keys()
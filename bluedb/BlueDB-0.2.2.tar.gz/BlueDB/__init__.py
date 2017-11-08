#Better BlueDB

__version__ = '0.2.1'

import _pickle as pickle
from collections.abc import MutableSequence, MutableMapping

"""
Current problems...

- Mutiple Blues
    At the moment, when two there are two instances of the same
    Blue database, and a value that already exists is changed or
    updated in one it doesnt update in the other, the other only updates
    when a key is created and __getitem__ is called to get said key

    a sync function was thought of to fix this problem but that would
    only work with two dicts only, instead what im thinking of is a
    class variable (not instance [self] variable) that goes through
    every database in that variable, (checks to see if the database =='s')
    and then updates any instances. This would be slow as hell tho...
"""

class Blue(MutableMapping):

    def __init__(self, name, **kwargs):
        """
        NeSTeD dIctS aND lISt!!!!
        """
        super().__init__()
        self.name = name
        self.file = self.name+'.blue'

        self.load_ = kwargs.pop('load', pickle.load)
        self.dump_ = kwargs.pop('dump', pickle.dump)

        self.body = {}

        try:
            with open(self.file, 'rb') as fp:
                data = self.load_(fp)
                for i in data.body.keys():
                    if type(data.body[i]) is dict:
                        blue = BlueDict(i, data.body[i], self)
                        self.body[i] = blue
                    elif type(data.body[i]) is list:
                        blue = BlueList(i, data.body[i], self)
                        self.body[i] = blue
                    else:
                        self.body[i] = data.body[i]
        except:
            self.dump_(self, open(self.file, 'wb'))
            self.body = {}

    def __getitem__(self, key):
        try:
            return self.body[key]
        except:
            with open(self.file, 'rb') as fp:
                data = self.load_(fp)
                self.body[key] = data
                return data.body[key]

    def __setitem__(self, key, value):
        if type(value) is dict:
            blue = BlueDict(key, value, self)
            self.body[key] = blue
        elif type(value) is list:
            blue = BlueList(key, value, self)
            self.body[key] = blue
        else:
            self.body[key] = value
        with open(self.file, 'wb') as fp:
            self.dump_(self, fp)

    def __delitem__(self, key):
        del self.body[key]
        with open(self.file, 'wb') as fp:
            self.dump_(self, fp)

    def __iter__(self):
        return iter(self.body)

    def __len__(self):
        return len(self.body)

    def __repr__(self):
        return str(self.body)

    def __str__(self):
        return str(self.body)

class BlueDict(MutableMapping):

    def __init__(self, key, value, previous):
        super().__init__()
        self.key = key
        self.body = {}
        self.previous = previous
        for i in value.keys():
            if type(value[i]) in (dict, list):
                self.__setitem__(i, value[i])
            else:
                self.body[i] = value[i]

    def insert(self, key, value):
        self.__setitem__(key, value)

    def __delitem__(self, key):
        self.body.__delitem__(key)
        if type(self.super['items'][key]) is dict:
            del self.super['dicts'][key]
        del self.super['items'][key]
        self.previous.__setitem__(self.key, self)

    def __len__(self):
        return len(self.items_)

    def __setitem__(self, key, value):
        if type(value) is dict:
            blue = BlueDict(key, value, self)
            self.body[key] = blue
        elif type(value) is list:
            blue = BlueList(key, value, self)
            self.body[key] = blue
        else:
            self.body[key] = value
        self.previous.__setitem__(self.key, self)

    def __getitem__(self, key):
        data = self.previous.__getitem__(self.key)
        return data.body[key]

    def __iter__(self):
        return iter(self.body)

    def __repr__(self):
        return str(self.body)

    def __str__(self):
        return str(self.body)

class BlueList(MutableSequence):

    def __init__(self, key, body, previous):
        super().__init__()
        self.key = key
        self.previous = previous
        self.body = []
        for i in body:
            self.append(i)

    def __setitem__(self, index, value):
        if type(value) is dict:
            blue = BlueDict(index, value, self)
        elif type(value) is list:
            blue = BlueList(index, value, self)
            self.body.__setitem__(index, value)
        self.body.__setitem__(index, value)
        self.previous.__setitem__(self.key, self)

    def __delitem__(self, index):
        self.body.__delitem__(index)

    def __getitem__(self, index):
        return self.body.__getitem__(index)

    def __len__(self):
        return len(self.body)

    def insert(self, index, value):
        self.body.insert(index, value)

    def __repr__(self):
        return str(self.body)

    def __str__(self):
        return str(self.body)

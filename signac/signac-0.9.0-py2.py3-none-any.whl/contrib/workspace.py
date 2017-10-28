import os
import errno
import re

import signac
from signac.contrib.hashing import calc_id


project = signac.get_project()


class Workspace:
    _valid_id = '[a-f0-9]{32}'

    def __init__(self, root):
        self._root = root

    @property
    def root(self):
        return str(self._root)

    def ids(self):
        m = re.compile(self._valid_id)
        try:
            for d in os.listdir(self._root):
                if m.match(d):
                    yield d
        except OSError as error:
            if error.errno != errno.ENOENT:
                raise

    def __iter__(self):
        return self.ids()

    def __len__(self):
        return len(list(self.ids()))

    def __getitem__(self, _id):
        if not re.match(self._valid_id, _id):
            raise ValueError(_id)
        return os.path.join(self._root, _id)

    def get_id(self):
        return  calc_id(''.join(sorted(self.ids())))

    def __repr__(self):
        return "{}(root='{}')".format(type(self).__name__, self.root)

    def __str__(self):
        return '<{} id={}... size={}>'.format(type(self).__name__, self.get_id()[:8], len(self))

wd = Workspace(project.workspace())
print(wd, repr(wd))
print(wd['0'*32])

for _id in wd:
    print(_id)
    break

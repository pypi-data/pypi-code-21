from fs.osfs import OSFS
from ..path.model import Path
from ..smartfs import FS


class File:
    def __init__(self, path, load_depth=0, fs=None):
        self.path = Path(path)
        if load_depth > 0:
            self.load(load_depth)
        else:
            self.contents = None
        self.fs = fs

    @property
    def exists(self):
        with FS(self.fs) as fs:
            return fs.exists(self.path.rel) and fs.isfile(self.path.rel)

    def load(self, depth):
        self.contents = None
        if depth < 0:
            return
        if not self.exists:
            raise FileNotFoundError(self.path.abs)
        if depth == 0:
            return
        with FS(self.fs) as fs:
            with fs.open(self.path.abs, 'rb') as fin:
                self.contents = fin.read()

    def save(self, data):
        with FS(self.fs) as fs:
            with fs.open(self.path.abs, 'wb') as fout:
                self.contents = fout.write(data)

    def to_serializable(self):
        try:
            cont = self.contents.decode() if self.contents else None
        except UnicodeDecodeError:
            cont = '!!binary' + str(self.contents)
        return {'path': self.path.abs,
                'name': self.path.name,
                'is_dir': False,
                'contents': cont}

    def __str__(self):
        import json
        return json.dumps(self.to_serializable(), sort_keys=True, separators=(',', ':'), indent=4)


class FileNotFound(Exception):
    def __init__(self, id_):
        self.id_ = id_
    def __str__(self):
        return 'File not found with id={}'.format(repr(self.id_))
    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.id_))


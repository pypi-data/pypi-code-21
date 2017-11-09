class DatamorphError(Exception):

    pass


class PathError(DatamorphError):

    def __init__(self, path, key, context):
        self.path = path
        self.key = key
        self.context = list(context)
        super().__init__(self.path)

    def serialize(self):
        return {
            'path': self.path,
            'key': self.key,
            'context': self.context
        }

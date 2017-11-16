import arrow

class Image():
    "A container image"
    def __init__(self, name, tag, hashtype=None, hashvalue=None):
        self.hashtype  = hashtype
        self.hashvalue = hashvalue
        self.name      = name
        self.tag       = tag

    def __str__(self):
        if self.hashtype and self.hashvalue:
            return f'{self.name}:{self.tag}@{self.hashtype}:{self.hashvalue}'
        else:
            return f'{self.name}:{self.tag}'

    def __eq__(self, other):
        if isinstance(other, str):
            other = Image(other)

        return all([
            self.name == other.name,
            self.tag == other.tag,
        ])

    @classmethod
    def parse(cls, value):
        start, _, hash_ = value.partition('@')
        name, _, tag = start.partition(':')
        hashtype, _, hashvalue = hash_.partition(':')
        return cls(name, tag, hashtype or None, hashvalue or None)

    def to_payload(self):
        return f'{self.name}:{self.tag}' if self.tag else self.name


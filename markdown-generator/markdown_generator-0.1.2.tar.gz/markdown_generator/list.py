class List(object):
    def __init__(self, ordered=False):
        self.items = []
        self.ordered = ordered

    def append(self, item):
        self.items.append(item)

    def __str__(self):
        marker = '1.' if self.ordered else '*'
        result = ''.join('{} {}\n'.format(marker, item) for item in self.items)
        return result + '\n'


class CheckList(object):
    def __init__(self):
        self.items = []

    def append(self, item, done=False):
        self.items.append((item, done))

    def __str__(self):
        lines = []
        for item, done in self.items:
            mark = 'x' if done else ' '
            lines.append('- [{}] {}\n'.format(mark, item))
        return ''.join(lines) + '\n'

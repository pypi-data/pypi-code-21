class Code(object):
    def __init__(self, language=None):
        self.language = language
        self.lines = []

    def append(self, text):
        self.lines.append(text)

    def __str__(self):
        lang = '' if self.language is None else self.language
        lines = []
        lines.append('```{}'.format(lang))
        lines.extend(self.lines)
        lines.append('```')
        return '\n'.join(lines) + '\n'

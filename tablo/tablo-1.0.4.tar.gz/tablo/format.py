

class AlignTemplate:

    def __init__(self, name, template):
        self.name = name
        self.template = template


class Align:
    Left = AlignTemplate('Left',     template='{sep}{sp}{{:{mgn}}}{sp}')
    Center = AlignTemplate('Center', template='{sep}{sp}{{:^{mgn}}}{sp}')
    Right = AlignTemplate('Right',   template='{sep}{sp}{{:>{mgn}}}{sp}')


class Format:
    def __init__(self, align, margin, spacer=' '):
        self.align = align
        self.margin = margin
        self.spacer = spacer

    def __repr__(self):
        return "Format(align={}, margin={}, spacer='{}')".format(
            self.align.name, self.margin, self.spacer)

    def __eq__(self, other):
        return all([
            self.align == other.align,
            self.margin == other.margin,
            self.spacer == other.spacer
        ])

    def copy(self):
        return Format(
            align=self.align,
            margin=self.margin,
            spacer=self.spacer)


def joinrow(formatted_sequence, separator='|'):
    result = ''
    for data, format in formatted_sequence:
        template = format.align.template.format(
            sp=format.spacer,
            sep=separator,
            mgn=format.margin)
        result += template.format(str(data))
    return result + separator

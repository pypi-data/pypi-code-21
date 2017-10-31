from dpcolors import ColorPart, ColorString


class BaseRegexParser:
    regex = None

    def process(self, match):
        raise NotImplementedError()  # PRAGMA: nocover


class BaseParser:
    markers = []
    special = []

    def parse(self, text):
        parts = []
        current_part = None
        current_text = ''
        while text:
            m = None
            for i in self.markers:
                m = i.regex.match(text)
                if m:
                    if current_part and current_text:
                        current_part.text = current_text
                        parts.append(current_part)
                    elif current_text:
                        parts.append(ColorPart(current_text))
                    current_part = i.process(m)
                    current_text = ''
                    break
            if not m:
                for i in self.special:
                    m = i.regex.match(text)
                    if m:
                        current_text += i.process(m)
                        break
            if not m:
                current_text += text[0]
                text = text[1:]
            else:
                text = text[m.end():]
        if current_text:
            if current_part:
                current_part.text = current_text
            else:
                current_part = ColorPart(current_text)
            parts.append(current_part)
        return ColorString(parts)

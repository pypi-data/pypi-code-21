import webbrowser


class File:
    def __init__(self, path, filename, extension):
        self.filename = filename
        self.path = path
        self.extension = extension

    def build(self):
        f = open(self.filepath(), 'w')
        f.write(str(self))
        f.close()

    def filepath(self):
        """Returns the formatted file path with filename and extension."""
        return f'{self.path}{self.filename}.{self.extension}'


class HTML(File):
    """Class representing an HTML file"""
    def __init__(self, path, filename, html, doctype='<!doctype html>'):
        File.__init__(self, path, filename, 'html')
        self.doctype = doctype
        self.html = html

    def openhtml(self):
        webbrowser.open_new(self.filepath())

    def __str__(self):
        return f'{self.doctype}\n' \
               f'{self.html.__str__(self.filepath())}\n'


class CSS(File):
    """Class representing a CSS file"""
    def __init__(self, path, filename, css, *args):
        File.__init__(self, path, filename, 'css')
        self.css = css

    def __str__(self):
        if isinstance(self.css, list):
            css_text = ''
            if len(self.css) != 0:
                for element in self.css:
                    css_text += f'\n{str(element)}\n'

            return css_text
        else:
            return str(self.css)


class JavaScript(File):
    """Class representing a Javascript file"""
    def __init__(self, path, filename, js, *args):
        File.__init__(self, path, filename, 'js')
        self.js = js

    def __str__(self):
        if isinstance(self.js, list):
            js_text = ''
            if len(self.js) != 0:
                for element in self.js:
                    js_text += f'\n{str(element)}\n'

            return js_text
        else:
            return str(self.js)

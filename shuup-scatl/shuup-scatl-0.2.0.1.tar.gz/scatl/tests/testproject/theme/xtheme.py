from shuup.xtheme import Theme as BaseTheme


class Xtheme(BaseTheme):
    identifier = 'scatl.tests.testproject.theme'
    name = 'Test Theme'
    template_dir = 'test'

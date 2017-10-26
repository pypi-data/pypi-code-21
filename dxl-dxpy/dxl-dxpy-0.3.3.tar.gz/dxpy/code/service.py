def template_path():
    from dxpy.filesystem import Path
    import dxpy
    p = Path(dxpy.__file__).father


class SnippetMaker:
    from . import snippet

    @classmethod
    def service(cls, name, path='.'):
        pass

    @classmethod
    def component(cls, name, path='.'):
        cls.snippet.Component(name, path).make()

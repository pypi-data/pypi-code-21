def template_path():
    from dxpy.filesystem import Path
    import dxpy
    p = Path(dxpy.__file__).father


class SnippetMaker:

    @classmethod
    def service(cls, name, path='.'):
        pass

    @classmethod
    def component(cls, name, path='.'):
        from . import snippet
        snippet.Component(name, path).make()

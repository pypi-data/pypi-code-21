from . import register_filter

try:
    import os
    from pathlib import Path
    from scss.compiler import Compiler

    @register_filter('sass')
    def sass_filter(bytes, cwd):
        """
            A sass compiler based on the Python scss module
        """
        compiler = Compiler(search_path=(cwd,))
        return compiler.compile_string(bytes)
except:
    from .utils import pipe

    @register_filter('sass')
    def sass_filter(bytes, cwd):
        """
            A sass compiler based on the sass executable
        """
        return pipe('sass --scss', bytes, cwd=cwd)

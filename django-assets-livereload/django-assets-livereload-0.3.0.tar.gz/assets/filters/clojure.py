from . import register_filter
from .utils import pipe

try:
    import shutil

    if shutil.which('clojure-compiler') is not None:
        @register_filter('clojure')
        def clojure_filter(bytes, cwd):
            """
            A JS minifier using Google's clojure compiler
            """
            return pipe('clojure-compiler', bytes, cwd=cwd)
    else:
        @register_filter('clojure')
        def clojure_filter(bytes, cwd):
            """
            A stub for Google's clojure compiler (the stub does nothing)
            """
            return bytes
except:
    @register_filter('clojure')
    def clojure_filter(bytes, cwd):
        """
        A stub for Google's clojure compiler (the stub does nothing)
        """
        return bytes

from . import register_filter
from .utils import pipe

try:
    import shutil

    if shutil.which('ttf2woff2') is not None:
        @register_filter('ttf2woff2')
        def ttf2woff2_filter(bytes, cwd):
            """
            A filter for converting ttf to woff2 fonts (based on google's woff2 library), installable via
            npm -g install ttf2woff2
            """
            return pipe('ttf2woff2', bytes, cwd=cwd)
    else:
        @register_filter('ttf2woff2')
        def ttf2woff2_filter(bytes, cwd):
            """
            A stub for ttf2woff2 converter (the stub does nothing)
            """
            return bytes
except:
    @register_filter('ttf2woff2')
    def ttf2woff2_filter(bytes, cwd):
        """
        A stub for ttf2woff2 converter (the stub does nothing)
        """
        return bytes



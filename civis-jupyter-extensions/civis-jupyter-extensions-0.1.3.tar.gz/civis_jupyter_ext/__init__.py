from .magics import load_ipython_extension  # noqa: F401
from .version import __version__  # noqa: F401


def _jupyter_nbextension_paths():
    return [{
        "section": "notebook",
        "src": "static",
        "dest": "civis_jupyter_ext",
        "require": "civis_jupyter_ext/index"
    }]

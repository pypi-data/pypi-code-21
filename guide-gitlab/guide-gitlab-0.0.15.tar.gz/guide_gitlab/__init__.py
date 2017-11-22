from .__about__ import __version__
from .gitlab import Gitlab3, Gitlab4
import guide_gitlab.exceptions as gitlab_exc 

__all__ = [__version__,
    Gitlab3,
    Gitlab4,
    gitlab_exc
]
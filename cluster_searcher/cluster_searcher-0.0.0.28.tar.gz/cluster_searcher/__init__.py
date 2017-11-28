__version__ = "0.0.0.28"


def __setup():
    from intermake import MENV
    
    MENV.name = "cluster_searcher"
    MENV.version = __version__


__setup()

from cluster_searcher import commands

def __setup():
    from intermake import MENV
    
    MENV.name = "cluster_searcher"
    MENV.version = "0.0.0.26"


__setup()

from cluster_searcher import commands
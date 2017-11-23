"""Entry point for standalone dataClay Execution Environment server.

The main can be called easily through a

    python -m dclay_server
"""

import dataclay.core
from . import main
import logging

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    
    dataclay.core.initialize()
    main()


import sys
from .buche import *
from .repr import *
from .event import *
from .debug import *


def _print_flush(x):
    print(x, flush=True)


master = MasterBuche(HRepr(), _print_flush)
buche = Buche(master, '/')
reader = Reader(sys.stdin)
read = reader.read

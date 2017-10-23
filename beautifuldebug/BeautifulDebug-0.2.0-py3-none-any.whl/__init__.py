# Version
version = '0.2.0'

from .utils import Dump
from .settings import Setting

setting = Setting()
dump = Dump(setting=setting).run

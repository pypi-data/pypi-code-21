__version__ = '1.2.2'
#从本文件夹里import models.py和exceptions.py
#from . import models, exceptions
from . import osskey
from . import wcc
#从本目录下api.py里import Service和Bucket这个类
#from .api import Service, Bucket
from .osskey import Osskey
from .utils import *
from .wcc import Wcc

import warnings
warnings.warn("nadds.fchdir is deprecated, please use os.fchdir() directly.",
              stacklevel=2)

from os import fchdir

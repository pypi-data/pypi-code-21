import sys

from .implementation import AEtestLoader

# replace this module with AEtestLoader instance
sys.modules[__name__] = loader = AEtestLoader()

# hardwire all module hidden attributes to loader instance
loader.__file__    = __file__
loader.__loader__  = __loader__
loader.__package__ = __package__
loader.__name__    = __name__
loader.__spec__    = __spec__
loader.__doc__     = __doc__
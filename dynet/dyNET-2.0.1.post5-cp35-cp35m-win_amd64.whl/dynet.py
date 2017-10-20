from __future__ import print_function
import sys
import dynet_config

HAVE_CUDA = False

_CONF = dynet_config.get()

if '--dynet-viz' in sys.argv:
    sys.argv.remove('--dynet-viz')
    from dynet_viz import *
else:
    def print_graphviz(**kwarge):
        print("Run with --dynet-viz to get the visualization behavior.")
    from _dynet import *

__version__ = 2.0

# check HAVE_CUDA
if not HAVE_CUDA:
    ERRMSG = 'DyNet was not installed with GPU support. Please see the installation instructions for how to make it possible to use GPUs.'
    if '--dynet-gpu' in sys.argv or '--dynet-gpus' in sys.argv:
        raise RuntimeError(ERRMSG)
    elif '--dynet-devices' in sys.argv:
        if 'GPU' in sys.argv[sys.argv.index('--dynet-devices')+1]:
            raise RuntimeError(ERRMSG)

if _CONF is None:
    init()
else:
    _params = DynetParams()
    _params.from_config(_CONF)
    _params.init()

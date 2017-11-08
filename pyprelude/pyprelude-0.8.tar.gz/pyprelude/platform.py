############################################################
#
# pyprelude.platform
# Copyright (C) 2017, Richard Cook
# Released under MIT License
# https://github.com/rcook/pyprelude
#
############################################################

import os
import sys

ON_LINUX = sys.platform.startswith("linux")
ON_MACOS = sys.platform.startswith("darwin")
ON_MSYS = (sys.platform.startswith("win") or sys.platform.startswith("msys")) and os.environ.get("SHELL", "").endswith("/bash")
ON_WINDOWS = sys.platform.startswith("win")

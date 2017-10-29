"""Support for coloured tracebacks.

This uses ``ultraTB``. The only thing it adds as that is automatically
enables the verbose coloured output.

"""


import sys
import os

from CleverSheep.Extras import ultraTB


mode = os.environ.get("ULTRATB", "")
if mode in ["colour", "color"]:
    sys.excepthook = ultraTB.ColorTB()
elif mode == "none":
    pass
elif mode in ["verbose", "detailed"]:
    sys.excepthook = ultraTB.VerboseTB()
else:
    sys.excepthook = ultraTB.ColorTB()

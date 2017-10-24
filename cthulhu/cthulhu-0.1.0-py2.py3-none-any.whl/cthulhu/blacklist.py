import numpy as np


def get_blacklist():
    return [
        "MWA001656-2559",
        "MWA005549-2621",
        "EXTmwacs13384",
        "MWA000806-2419A",
    ]


def bad_sources(sources):
    blacklist = get_blacklist()
    return np.in1d(sources, blacklist)

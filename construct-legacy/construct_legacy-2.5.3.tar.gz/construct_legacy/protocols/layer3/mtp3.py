"""
Message Transport Part 3 (SS7 protocol stack)
(untested)
"""
from construct_legacy import *


mtp3_header = BitStruct("mtp3_header",
    Nibble("service_indicator"),
    Nibble("subservice"),
)


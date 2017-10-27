"""
Contains global settings from the tool
Might be changed for the use of .ini
"""

import os

# Path to local data
LOCAL_DATA = os.path.dirname(__file__) + "/data"
# Length max for unknown spacer
SPACER_MAX = 150
# number of nucleotide to keep when truncation occurs
NUC_LEFT = 10
# Character for begining of SPACER
START_CHAR = "-"
# Characeter for end of SPACER
END_CHAR = "&"
# Name for spacers found with positions
FOUND_SPAC = "found_spacers.bed"
# Name for new spacer sequences FASTA file
NEW_SPAC = "new_spacers.fa"

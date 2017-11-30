import re

# General Pattern for detecting granules
_granule_pattern = re.compile(r'(S1[A-D]_\w\w_(GRD|SLC|OCN)\w_[12]\w{3}_\w{15}_\w{15}_\w{6}_\w{6}_\w{4})')

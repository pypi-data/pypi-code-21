import sys
from cpymad.madx import Madx

m = Madx()
m.verbose(False)
m.call(sys.argv[1], True)

for seq in m.sequences.values():
    if not seq.is_expanded:
        seq.beam = {}
        seq.use()
    print(seq.name, len(seq.expanded_elements))

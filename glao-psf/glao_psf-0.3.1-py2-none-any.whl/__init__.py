import os
d = os.path.abspath(__file__)
d = os.path.dirname(d)
d = os.path.join(d,'_version.py')
execfile(d)
